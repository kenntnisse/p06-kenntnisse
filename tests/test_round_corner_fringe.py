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
    async def test_transparent_corner_edge_is_anti_aliased(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(60,255,255,255,1)",
            mode="RGBA",
        )
        image = image.convert("RGBA")

        # Pixels in a ring around the top-left arc (radius 60, centre
        # (60, 60)). The anti-aliased edge must have partial alpha, so at
        # least one pixel in the ring has alpha between 1 and 254.
        ring_alphas = []
        for y in range(0, 60):
            for x in range(0, 60):
                dist = math.hypot(x - 60, y - 60)
                if not 59.0 <= dist <= 62.0:
                    continue
                ring_alphas.append(image.getpixel((x, y))[3])

        assert any(0 < a < 255 for a in ring_alphas), (
            "no partly transparent pixels on the corner arc; "
            f"alpha values in ring: {sorted(set(ring_alphas))}"
        )
