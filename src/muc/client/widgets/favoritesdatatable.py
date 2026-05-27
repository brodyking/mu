from muc.client.widgets.tracksdatatable import TracksDataTable


class FavoritesDataTable(TracksDataTable):
    def on_show(self) -> None:
        self.call_after_refresh(self._filter_to_favorites)

    def _filter_to_favorites(self) -> None:
        table = self.main_table
        table.clear()
        for row in self.full_rows:
            if row[1] == "❤":
                table.add_row(*row, key=str(row[0]))

    def filter_table(self, search_term: str) -> None:
        # Temporarily swap full_rows to only favorites, then restore
        all_rows = self.full_rows
        self.full_rows = [row for row in all_rows if row[1] == "❤"]
        super().filter_table(search_term)
        self.full_rows = all_rows

    def set_track_favorite(self, track_id, is_favorite) -> None:
        super().set_track_favorite(track_id, is_favorite)

        # Update full_rows to reflect the new favorite status
        for i, row in enumerate(self.full_rows):
            if row[0] == track_id:
                self.full_rows[i] = row[:1] + ("❤" if is_favorite else " ",) + row[2:]
                break

        # Add or remove the row from the visible table
        if is_favorite:
            row = next((r for r in self.full_rows if r[0] == track_id), None)
            if row:
                try:
                    self.main_table.add_row(*row, key=str(track_id))
                except Exception:
                    pass  # Row already exists
        else:
            try:
                self.main_table.remove_row(str(track_id))
            except Exception:
                pass  # Row didn't exist
