"""
Discovery Agent - Searches academic sources for papers.
"""
import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import arxiv

logger = logging.getLogger("research_app.agents.discovery")


def search_arxiv(
    query: str,
    max_papers: int = 10,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search arXiv for research papers matching the given query."""
    logger.info(f"ArXiv search: query={query}, max={max_papers}, from={from_date}, to={to_date}")

    try:
        categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]
        category_filter = " OR ".join([f"cat:{cat}" for cat in categories])
        full_query = f"({query}) AND ({category_filter})"

        if from_date or to_date:
            from_arxiv = (
                datetime.strptime(from_date, "%Y-%m-%d").strftime("%Y%m%d0000")
                if from_date
                else "202001010000"
            )
            to_arxiv = (
                datetime.strptime(to_date, "%Y-%m-%d").strftime("%Y%m%d2359")
                if to_date
                else datetime.now().strftime("%Y%m%d2359")
            )
            date_filter = f"submittedDate:[{from_arxiv} TO {to_arxiv}]"
            full_query = f"{full_query} AND {date_filter}"

        search = arxiv.Search(
            query=full_query,
            max_results=max_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        results = list(search.results())
        papers = []

        for result in results:
            paper = {
                "id": result.get_short_id(),
                "title": result.title,
                "link": result.entry_id,
                "metadata": {
                    "authors": [
                        {"name": author.name, "affiliation": ""}
                        for author in result.authors
                    ],
                    "abstract": result.summary.replace("\n", " ").strip(),
                    "published_date": result.published.isoformat(),
                    "updated_date": result.updated.isoformat(),
                    "categories": result.categories,
                    "source": "arxiv",
                    "doi": getattr(result, "doi", None),
                    "comment": getattr(result, "comment", None),
                    "journal_ref": getattr(result, "journal_ref", None),
                },
            }
            papers.append(paper)

        logger.info(f"ArXiv search completed: {len(papers)} papers found")
        return papers

    except Exception as e:
        logger.error(f"ArXiv search failed: {e}")
        return []


def discover_and_process_papers(
    query: str,
    max_papers: int = 10,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Complete discovery workflow: search, deduplicate, validate."""
    logger.info(f"Starting discovery workflow: query={query}")
    start_time = time.time()

    try:
        papers = search_arxiv(query, max_papers, from_date, to_date)

        # Deduplicate
        unique_papers = []
        seen_titles = set()
        for paper in papers:
            normalized = re.sub(r"\s+", " ", paper["title"].lower().strip())
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique_papers.append(paper)

        # Validate
        valid_papers = [
            p
            for p in unique_papers
            if p.get("title")
            and p.get("metadata", {}).get("abstract")
            and len(p.get("metadata", {}).get("abstract", "")) >= 50
        ]

        processing_time = time.time() - start_time
        statistics = {
            "initial_count": len(papers),
            "after_deduplication": len(unique_papers),
            "final_count": len(valid_papers),
            "duplicates_removed": len(papers) - len(unique_papers),
            "invalid_removed": len(unique_papers) - len(valid_papers),
            "processing_time": f"{processing_time:.2f}s",
        }

        return {
            "processed_papers": valid_papers,
            "statistics": statistics,
            "source_counts": {"arxiv": len(valid_papers), "ieee": 0, "acl": 0},
            "search_metadata": {
                "query_used": query,
                "date_range": f"{from_date} to {to_date}" if from_date or to_date else "all_time",
                "sources_searched": ["arxiv"],
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time": f"{processing_time:.2f}s",
            },
        }

    except Exception as e:
        logger.error(f"Discovery workflow failed: {e}")
        return {
            "processed_papers": [],
            "statistics": {"error": str(e)},
            "source_counts": {"arxiv": 0, "ieee": 0, "acl": 0},
            "search_metadata": {"error": str(e)},
        }
