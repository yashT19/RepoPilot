from pathlib import Path
import re


class CodeChangeApplier:

    # ==================================================
    # Apply Code Change
    # ==================================================

    def apply_change(
        self,
        repository_path: str,
        file_path: str,
        original_code: str,
        proposed_code: str
    ) -> dict:

        # --------------------------------------------------
        # 1. Normalize file path
        # --------------------------------------------------

        normalized_file_path = file_path.replace(
            "\\",
            "/"
        )

        # --------------------------------------------------
        # 2. Build full file path
        # --------------------------------------------------

        full_path = (
            Path(repository_path)
            / "extracted"
            / normalized_file_path
        )

        # --------------------------------------------------
        # 3. Validate file exists
        # --------------------------------------------------

        if not full_path.exists():

            return {
                "success": False,
                "message": (
                    f"File not found: {file_path}"
                )
            }

        # --------------------------------------------------
        # 4. Read existing file content
        # --------------------------------------------------

        content = full_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        # --------------------------------------------------
        # 5. Normalize line endings
        # --------------------------------------------------

        normalized_content = content.replace(
            "\r\n",
            "\n"
        )

        normalized_original_code = (
            original_code
            .replace("\r\n", "\n")
            .strip()
        )

        normalized_proposed_code = (
            proposed_code
            .replace("\r\n", "\n")
            .strip()
        )

        # --------------------------------------------------
        # 6. Try exact match first
        # --------------------------------------------------

        match = re.search(
            re.escape(normalized_original_code),
            normalized_content
        )

        # --------------------------------------------------
        # 7. If exact match fails, allow indentation
        # and whitespace differences
        # --------------------------------------------------

        if not match:

            lines = (
                normalized_original_code
                .split("\n")
            )

            pattern_lines = []

            for line in lines:

                stripped_line = line.strip()

                # Ignore indentation differences
                escaped_line = re.escape(
                    stripped_line
                )

                pattern_lines.append(
                    r"[ \t]*"
                    + escaped_line
                    + r"[ \t]*"
                )

            flexible_pattern = (
                r"\s*\n\s*".join(
                    pattern_lines
                )
            )

            match = re.search(
                flexible_pattern,
                normalized_content
            )

        # --------------------------------------------------
        # 8. Original code still not found
        # --------------------------------------------------

        if not match:

            return {
                "success": False,
                "message": (
                    "Original code was not found in the "
                    "file. The change was not applied."
                ),
                "file_path": str(full_path),
                "original_code": original_code
            }

        # --------------------------------------------------
        # 9. Create backup before modification
        # --------------------------------------------------

        backup_path = full_path.with_suffix(
            full_path.suffix + ".backup"
        )

        backup_path.write_text(
            content,
            encoding="utf-8"
        )

        # --------------------------------------------------
        # 10. Preserve base indentation
        # --------------------------------------------------

        matched_code = match.group()

        first_line = (
            matched_code
            .split("\n")[0]
        )

        indentation_match = re.match(
            r"^[ \t]*",
            first_line
        )

        base_indentation = (
            indentation_match.group()
            if indentation_match
            else ""
        )

        # --------------------------------------------------
        # 11. Apply indentation to proposed code
        #
        # The first line gets the indentation of the
        # matched code. Other lines preserve their
        # relative indentation from the LLM response.
        # --------------------------------------------------

        proposed_lines = (
            normalized_proposed_code
            .split("\n")
        )

        indented_proposed_lines = []

        for line in proposed_lines:

            if line.strip():

                indented_proposed_lines.append(
                    base_indentation + line
                )

            else:

                indented_proposed_lines.append(
                    ""
                )

        indented_proposed_code = "\n".join(
            indented_proposed_lines
        )

        # --------------------------------------------------
        # 12. Apply change
        # --------------------------------------------------

        updated_content = (
            normalized_content[:match.start()]
            + indented_proposed_code
            + normalized_content[match.end():]
        )

        # --------------------------------------------------
        # 13. Write updated content
        # --------------------------------------------------

        full_path.write_text(
            updated_content,
            encoding="utf-8"
        )

        return {
            "success": True,
            "message": (
                "Code change applied successfully."
            ),
            "file_path": str(full_path),
            "backup_path": str(backup_path)
        }

    # ==================================================
    # Restore File From Backup
    # ==================================================

    def restore_backup(
        self,
        file_path: str,
        backup_path: str
    ) -> dict:

        # --------------------------------------------------
        # 1. Convert paths
        # --------------------------------------------------

        original_file = Path(file_path)
        backup_file = Path(backup_path)

        # --------------------------------------------------
        # 2. Validate original file
        # --------------------------------------------------

        if not original_file.exists():

            return {
                "success": False,
                "message": (
                    f"Original file not found: "
                    f"{file_path}"
                )
            }

        # --------------------------------------------------
        # 3. Validate backup file
        # --------------------------------------------------

        if not backup_file.exists():

            return {
                "success": False,
                "message": (
                    f"Backup file not found: "
                    f"{backup_path}"
                )
            }

        try:

            # --------------------------------------------------
            # 4. Read backup content
            # --------------------------------------------------

            backup_content = backup_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            # --------------------------------------------------
            # 5. Restore original file
            # --------------------------------------------------

            original_file.write_text(
                backup_content,
                encoding="utf-8"
            )

            return {
                "success": True,
                "message": (
                    "File restored successfully "
                    "from backup."
                ),
                "file_path": str(original_file),
                "backup_path": str(backup_file)
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Failed to restore file from "
                    f"backup: {str(error)}"
                )
            }