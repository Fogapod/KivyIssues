# -*- coding: utf-8 -*-
#
# Пагинатор страниц.
#

__version__ = "0.01"


def paginator(total_number_pages, select_number_page):
    """
    type total_number_pages: int;
    param total_number_pages: 558;

    type select_number_page: int;
    param select_number_page: 16;

    return: list - ['1', '2', '3', '...', '14', '15', '[16]', '17', '18',
                    '...', '556', '557', '558']

    """

    assert (0 < total_number_pages)
    assert (0 < select_number_page <= total_number_pages)

    # Build set of pages to display.
    if total_number_pages <= 10:
        build_pages = set(range(1, total_number_pages + 1))
    else:
        build_pages = \
            (set(range(1, 4)) | set(range(max(1, select_number_page - 2),
                                          min(select_number_page + 3,
                                              total_number_pages + 1))) |
             set(range(total_number_pages - 2, total_number_pages + 1)))

    # Display pages.
    def display():
        last_page = 0

        for page in sorted(build_pages):
            if page != last_page + 1:
                yield "..."
            yield ("[{}]" if page == select_number_page else "{}").format(
                page
            )
            last_page = page

    return list(display())


if __name__ in ("__main__", "__android__"):
    print(paginator(558, 16))
