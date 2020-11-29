from django.core.paginator import Paginator


class CustomPaginator(Paginator):

    def range_generator(self, current_page, page_count, dist=1):
        yield 1
        last = 1
        startRange = (1, 1)
        currentRange = (
            current_page - dist, current_page + dist
        )
        endRange = (page_count, page_count)
        for r in (startRange, currentRange, endRange):
            if r[0] > last + 1:
                yield 0
            rangeStart = max(min(page_count, r[0]), last + 1)
            rangeEnd = min(page_count, r[1])
            if rangeStart <= rangeEnd:
                for p in range(rangeStart, rangeEnd + 1):
                    yield p
                last = rangeEnd

    def range_by_distance(self, page, distance=1):
        return self.range_generator(page.number, self.num_pages, dist=distance)

    def page(self, number):
        try:
            retval = super(CustomPaginator, self).page(number)
        except:  # noqa
            if int(number) > self.num_pages:
                number = self.num_pages
            else:
                number = 1
            retval = super(CustomPaginator, self).page(number)

        retval.pagination_list = self.range_by_distance(retval)
        return retval
