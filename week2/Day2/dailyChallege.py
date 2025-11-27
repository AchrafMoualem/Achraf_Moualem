#Daily Challenge : Pagination
import math

class Pagination:
    def __init__(self, items=None, page_size=10):
        if items == None:
            items = []
        self.items = items
        self.page_size = page_size
        self.current_idx = 0
        self.total_pages = math.ceil(len(self.items) / self.page_size) if self.items else 0

    def get_visible_items(self):
        if not self.items:
            return []
        start_idx = self.current_idx * self.page_size
        end_idx = start_idx + self.page_size
        return self.items[start_idx:end_idx]

    def go_to_page(self, page_num):
        target_idx = page_num - 1
        if page_num < 1 or page_num > self.total_pages:
            raise ValueError(f"Page {page_num} is out of range. Valid pages: 1 to {self.total_pages}")
        self.current_idx = target_idx
        return self

    def first_page(self):
        self.current_idx = 0
        return self

    def last_page(self):
        if self.total_pages > 0:
            self.current_idx = self.total_pages - 1
        return self

    def next_page(self):
        if self.current_idx < self.total_pages - 1:
            self.current_idx += 1
        return self

    def previous_page(self):
        if self.current_idx > 0:
            self.current_idx -= 1
        return self

    def __str__(self):
        return f"Page {self.current_idx + 1}/{self.total_pages}"

    def get_current_page(self):
        return self.current_idx + 1


items = list("abcdefghijklmnopqrstuvwxy")  # [1, 2, 3, ..., 15]
pagination = Pagination(items=items, page_size=4)

print("Start:", pagination)
print("Items:", pagination.get_visible_items())

pagination.next_page()
print("Next page:", pagination.get_visible_items())

pagination.previous_page()
print("Back to first:", pagination.get_visible_items())

pagination.go_to_page(3)
print("Page 3:", pagination.get_visible_items())

pagination.last_page()
print("Last page:", pagination.get_visible_items())

pagination.first_page()
print("First page:", pagination.get_visible_items())

# Method chaining
pagination.first_page().next_page().next_page()
print("Chained to page 3:", pagination.get_visible_items())

# Error test
try:
    pagination.go_to_page(10)
except ValueError as e:
    print("Error:", e)