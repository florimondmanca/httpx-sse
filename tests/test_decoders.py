from httpx_sse._decoders import SSELineDecoder, _splitlines_sse


class TestSplitlinesSSE:
    def test_crlf_splitting(self) -> None:
        text = "line1\r\nline2\r\nline3"
        lines = _splitlines_sse(text)
        assert lines == ["line1", "line2", "line3"]

    def test_cr_splitting(self) -> None:
        text = "line1\rline2\rline3"
        lines = _splitlines_sse(text)
        assert lines == ["line1", "line2", "line3"]

    def test_lf_splitting(self) -> None:
        text = "line1\nline2\nline3"
        lines = _splitlines_sse(text)
        assert lines == ["line1", "line2", "line3"]

    def test_mixed_line_endings(self) -> None:
        text = "line1\r\nline2\nline3\rline4"
        lines = _splitlines_sse(text)
        assert lines == ["line1", "line2", "line3", "line4"]

    def test_empty_lines(self) -> None:
        text = "line1\n\nline3"
        lines = _splitlines_sse(text)
        assert lines == ["line1", "", "line3"]

    def test_unicode_line_separator_not_split(self) -> None:
        # U+2028 (LINE SEPARATOR) should NOT be treated as a newline
        text = "line1\u2028line2"
        lines = _splitlines_sse(text)
        assert lines == ["line1\u2028line2"]

    def test_unicode_paragraph_separator_not_split(self) -> None:
        # U+2029 (PARAGRAPH SEPARATOR) should NOT be treated as a newline
        text = "line1\u2029line2"
        lines = _splitlines_sse(text)
        assert lines == ["line1\u2029line2"]

    def test_unicode_next_line_not_split(self) -> None:
        # U+0085 (NEXT LINE) should NOT be treated as a newline
        text = "line1\u0085line2"
        lines = _splitlines_sse(text)
        assert lines == ["line1\u0085line2"]

    def test_empty_string(self) -> None:
        lines = _splitlines_sse("")
        assert lines == []

    def test_only_newlines(self) -> None:
        lines = _splitlines_sse("\n\r\n\r")
        assert lines == ["", "", ""]

    def test_trailing_newlines(self) -> None:
        lines = _splitlines_sse("line1\n")
        assert lines == ["line1"]


class TestSSELineDecoder:
    def _decode_chunks(self, chunks: list[str]) -> list[str]:
        """Helper to decode a list of chunks and return all lines."""
        decoder = SSELineDecoder()
        lines = []
        for chunk in chunks:
            lines.extend(decoder.decode(chunk))
        lines.extend(decoder.flush())
        return lines

    def test_basic_lines(self) -> None:
        chunks = ["line1\nline2\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_incremental_decoding(self) -> None:
        chunks = ["partial", " line\n", "another\n"]
        assert self._decode_chunks(chunks) == ["partial line", "another"]

    def test_trailing_cr_with_immediate_n(self) -> None:
        # \r at end of first chunk, \n at start of second chunk
        chunks = ["line1\r", "\nline2", "\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_crlf_across_chunks(self) -> None:
        # \r\n split across two chunks
        chunks = ["line1\r", "\nline2\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_buffer_without_newline(self) -> None:
        # Text without newline should be buffered then flushed
        chunks = ["buffered"]
        assert self._decode_chunks(chunks) == ["buffered"]

    def test_buffer_with_newline(self) -> None:
        # Text without newline followed by newline
        chunks = ["buffered", "\n"]
        assert self._decode_chunks(chunks) == ["buffered"]

    def test_no_flush_needed(self) -> None:
        # All lines terminated, flush returns nothing
        chunks = ["line1\n", "line2\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_flush_with_trailing_cr(self) -> None:
        # Text ending with \r should not leave buffered content after flush
        chunks = ["text\r"]
        assert self._decode_chunks(chunks) == ["text"]

    def test_empty_chunks(self) -> None:
        # Empty chunks should be handled gracefully
        chunks = ["", "line1\n", "", "line2\n", ""]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_multiple_empty_lines(self) -> None:
        chunks = ["\n\n\n"]
        assert self._decode_chunks(chunks) == ["", "", ""]

    def test_mixed_line_endings_incremental(self) -> None:
        chunks = ["line1\r\n", "line2\r", "line3\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2", "line3"]

    def test_partial_line_then_complete(self) -> None:
        chunks = ["par", "tial", " line\ncomp", "lete\n"]
        assert self._decode_chunks(chunks) == ["partial line", "complete"]

    def test_unicode_line_separators_preserved(self) -> None:
        # Unicode line separators should be preserved in the output
        chunks = ["data\u2028field\nline2\u2029end\n"]
        assert self._decode_chunks(chunks) == ["data\u2028field", "line2\u2029end"]

    def test_alternating_cr_lf(self) -> None:
        chunks = ["\r\n\r\n"]
        assert self._decode_chunks(chunks) == ["", ""]

    def test_flush_after_partial(self) -> None:
        chunks = ["line1\npartial"]
        assert self._decode_chunks(chunks) == ["line1", "partial"]

    def test_consecutive_cr_handling(self) -> None:
        chunks = ["line1\r\rline2\n"]
        assert self._decode_chunks(chunks) == ["line1", "", "line2"]

    def test_text_after_trailing_newline(self) -> None:
        chunks = ["line1\n", "line2", "\n"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_only_cr(self) -> None:
        chunks = ["\r", "\r"]
        assert self._decode_chunks(chunks) == ["", ""]

    def test_only_lf(self) -> None:
        chunks = ["\n"]
        assert self._decode_chunks(chunks) == [""]

    def test_empty_input(self) -> None:
        assert self._decode_chunks([]) == []

    def test_single_char_chunks(self) -> None:
        # Test with single character chunks to ensure buffering works
        chunks = ["h", "e", "l", "l", "o", "\n", "w", "o", "r", "l", "d"]
        assert self._decode_chunks(chunks) == ["hello", "world"]

    def test_cr_lf_as_separate_chunks(self) -> None:
        # Each character as separate chunk
        chunks = ["l", "i", "n", "e", "1", "\r", "\n", "l", "i", "n", "e", "2"]
        assert self._decode_chunks(chunks) == ["line1", "line2"]

    def test_mixed_endings_with_content(self) -> None:
        chunks = ["a\rb\nc\r\nd"]
        assert self._decode_chunks(chunks) == ["a", "b", "c", "d"]

    def test_trailing_cr_no_followup(self) -> None:
        # Trailing \r with no following text
        chunks = ["line\r"]
        assert self._decode_chunks(chunks) == ["line"]

    def test_complex_mixed_scenario(self) -> None:
        # Complex scenario with various line endings and partial chunks
        chunks = [
            "first",
            " line\r",
            "\nsecond",
            " line\r\n",
            "third\rfo",
            "urth\n",
            "fifth",
        ]
        assert self._decode_chunks(chunks) == [
            "first line",
            "second line",
            "third",
            "fourth",
            "fifth",
        ]
