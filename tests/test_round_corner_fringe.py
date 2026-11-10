# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import math

from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerFringeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_corner_edge_is_not_dark(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(60,255,255,255,1)",
            mode="RGBA",
        )
        image = image.convert("RGBA")
        source = self.get_fixture("source.jpg").convert("RGB")

        # Only pixels in a thin band just inside the arc of the top-left
        # corner (radius 60, centre (60, 60)). Edge pixels in this band
        # must keep the source colour. They may be partly transparent,
        # but they must not be opaque and darkened.
        darkened = []
        for y in range(0, 60):
            for x in range(0, 60):
                dist = math.hypot(x - 60, y - 60)
                if not 59.0 <= dist <= 60.0:
                    continue
                r, g, b, a = image.getpixel((x, y))
                if a != 255:
                    continue
                sr, sg, sb = source.getpixel((x, y))
                if (r < sr - 30) or (g < sg - 30) or (b < sb - 30):
                    darkened.append((x, y, (r, g, b, a), (sr, sg, sb)))

        assert not darkened, (
            f"{len(darkened)} opaque edge pixels darker than the source, "
            f"first few: {darkened[:5]}"
        )
