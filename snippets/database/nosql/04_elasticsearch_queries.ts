// ============================================================================
// Elasticsearch Queries - Full-text Search and Analytics
// ============================================================================

import { Client } from '@elastic/elasticsearch';

const client = new Client({ node: 'http://localhost:9200' });

// Snippet 1: Simple match query
async function searchProducts(query: string) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        match: {
          name: query
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 2: Multi-match query across fields
async function multiFieldSearch(query: string) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        multi_match: {
          query,
          fields: ['name^3', 'description^2', 'tags'],
          type: 'best_fields',
          fuzziness: 'AUTO'
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 3: Bool query with multiple conditions
async function advancedProductSearch(params: any) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        bool: {
          must: [
            { match: { category: params.category } }
          ],
          filter: [
            { range: { price: { gte: params.minPrice, lte: params.maxPrice } } },
            { term: { inStock: true } }
          ],
          should: [
            { match: { tags: params.preferredTag } }
          ],
          must_not: [
            { term: { discontinued: true } }
          ],
          minimum_should_match: 1
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 4: Aggregations for analytics
async function getProductStatistics() {
  const result = await client.search({
    index: 'products',
    body: {
      size: 0,
      aggs: {
        categories: {
          terms: {
            field: 'category.keyword',
            size: 10
          },
          aggs: {
            avg_price: {
              avg: { field: 'price' }
            },
            price_stats: {
              stats: { field: 'price' }
            }
          }
        },
        price_ranges: {
          range: {
            field: 'price',
            ranges: [
              { to: 50 },
              { from: 50, to: 100 },
              { from: 100, to: 500 },
              { from: 500 }
            ]
          }
        }
      }
    }
  });

  return result.aggregations;
}

// Snippet 5: Date histogram aggregation
async function getSalesOverTime() {
  const result = await client.search({
    index: 'orders',
    body: {
      size: 0,
      query: {
        range: {
          orderDate: {
            gte: 'now-1y/d'
          }
        }
      },
      aggs: {
        sales_over_time: {
          date_histogram: {
            field: 'orderDate',
            calendar_interval: 'month'
          },
          aggs: {
            total_revenue: {
              sum: { field: 'totalAmount' }
            },
            avg_order_value: {
              avg: { field: 'totalAmount' }
            }
          }
        }
      }
    }
  });

  return result.aggregations;
}

// Snippet 6: Nested query for complex documents
async function searchOrdersByProduct(productName: string) {
  const result = await client.search({
    index: 'orders',
    body: {
      query: {
        nested: {
          path: 'items',
          query: {
            match: {
              'items.productName': productName
            }
          },
          inner_hits: {}
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 7: Highlighting search results
async function searchWithHighlight(query: string) {
  const result = await client.search({
    index: 'articles',
    body: {
      query: {
        multi_match: {
          query,
          fields: ['title', 'content']
        }
      },
      highlight: {
        fields: {
          title: {
            pre_tags: ['<mark>'],
            post_tags: ['</mark>']
          },
          content: {
            pre_tags: ['<mark>'],
            post_tags: ['</mark>'],
            fragment_size: 150,
            number_of_fragments: 3
          }
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 8: Fuzzy search for typos
async function fuzzySearch(query: string) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        fuzzy: {
          name: {
            value: query,
            fuzziness: 2,
            prefix_length: 1,
            max_expansions: 100
          }
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 9: Autocomplete with prefix query
async function autocomplete(prefix: string) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        prefix: {
          'name.keyword': prefix
        }
      },
      size: 10
    }
  });

  return result.hits.hits.map(hit => hit._source.name);
}

// Snippet 10: Geospatial search
async function findNearbyStores(lat: number, lon: number, distance: string = '10km') {
  const result = await client.search({
    index: 'stores',
    body: {
      query: {
        bool: {
          filter: {
            geo_distance: {
              distance,
              location: {
                lat,
                lon
              }
            }
          }
        }
      },
      sort: [
        {
          _geo_distance: {
            location: {
              lat,
              lon
            },
            order: 'asc',
            unit: 'km'
          }
        }
      ]
    }
  });

  return result.hits.hits;
}

// Snippet 11: More Like This query
async function findSimilarProducts(productId: string) {
  const result = await client.search({
    index: 'products',
    body: {
      query: {
        more_like_this: {
          fields: ['name', 'description', 'tags'],
          like: [
            {
              _index: 'products',
              _id: productId
            }
          ],
          min_term_freq: 1,
          max_query_terms: 12,
          min_doc_freq: 1
        }
      }
    }
  });

  return result.hits.hits;
}

// Snippet 12: Scroll API for large result sets
async function scrollAllProducts() {
  let allProducts: any[] = [];

  const initialResponse = await client.search({
    index: 'products',
    scroll: '1m',
    body: {
      size: 1000,
      query: { match_all: {} }
    }
  });

  allProducts = allProducts.concat(initialResponse.hits.hits);
  let scrollId = initialResponse._scroll_id;

  while (true) {
    const scrollResponse = await client.scroll({
      scroll_id: scrollId,
      scroll: '1m'
    });

    if (scrollResponse.hits.hits.length === 0) {
      break;
    }

    allProducts = allProducts.concat(scrollResponse.hits.hits);
    scrollId = scrollResponse._scroll_id;
  }

  // Clear scroll
  await client.clearScroll({ scroll_id: scrollId });

  return allProducts;
}

// Snippet 13: Composite aggregation for pagination
async function getPaginatedAggregation(afterKey?: any) {
  const result = await client.search({
    index: 'products',
    body: {
      size: 0,
      aggs: {
        products_by_category: {
          composite: {
            size: 100,
            sources: [
              { category: { terms: { field: 'category.keyword' } } },
              { brand: { terms: { field: 'brand.keyword' } } }
            ],
            after: afterKey
          },
          aggs: {
            total_sales: {
              sum: { field: 'salesCount' }
            }
          }
        }
      }
    }
  });

  return result.aggregations.products_by_category;
}

// Snippet 14: Suggest API for autocomplete
async function getSuggestions(prefix: string) {
  const result = await client.search({
    index: 'products',
    body: {
      suggest: {
        product_suggest: {
          prefix,
          completion: {
            field: 'name_suggest',
            size: 10,
            fuzzy: {
              fuzziness: 'AUTO'
            }
          }
        }
      }
    }
  });

  return result.suggest.product_suggest[0].options;
}

// Snippet 15: Bulk indexing
async function bulkIndexDocuments(documents: any[]) {
  const body = documents.flatMap(doc => [
    { index: { _index: 'products', _id: doc.id } },
    doc
  ]);

  const result = await client.bulk({ body, refresh: true });

  return {
    indexed: result.items.filter(item => !item.index?.error).length,
    errors: result.items.filter(item => item.index?.error)
  };
}

// Snippet 16: Update by query
async function updatePricesByCategory(category: string, priceMultiplier: number) {
  const result = await client.updateByQuery({
    index: 'products',
    body: {
      query: {
        term: {
          'category.keyword': category
        }
      },
      script: {
        source: `ctx._source.price = ctx._source.price * params.multiplier`,
        params: {
          multiplier: priceMultiplier
        }
      }
    }
  });

  return result.updated;
}

// Snippet 17: Delete by query
async function deleteOldLogs(daysOld: number) {
  const result = await client.deleteByQuery({
    index: 'logs',
    body: {
      query: {
        range: {
          timestamp: {
            lt: `now-${daysOld}d`
          }
        }
      }
    }
  });

  return result.deleted;
}

// Snippet 18: Percolator for reverse search
async function registerAlert(alertId: string, alertQuery: any) {
  await client.index({
    index: 'product_alerts',
    id: alertId,
    body: {
      query: alertQuery
    }
  });
}

async function checkProductAgainstAlerts(product: any) {
  const result = await client.search({
    index: 'product_alerts',
    body: {
      query: {
        percolate: {
          field: 'query',
          document: product
        }
      }
    }
  });

  return result.hits.hits;
}
