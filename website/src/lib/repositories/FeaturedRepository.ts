import type { Featured } from "../../types/featured";

import featuredData from "../../data/home/featured.json";

const featured = featuredData as Featured;

export default class FeaturedRepository {

    static get(): Featured {
        return featured;
    }

}