import sys
import time
from typing import List, Optional

from src.entity.config_entity import MongoDBConfig
from src.exception.base import CustomException
from src.logger.logging_setup import ensure_context_id, new_task_id

from .mongo_base import MongoBaseRepository


class ProducerRepository(MongoBaseRepository):

    def __init__(
            self,
            mongo_db_config: MongoDBConfig,
            job_id: Optional[str] = None,
            task_id: Optional[str] = None,
            context_id: Optional[str] = None,
            parent_context_id: Optional[str] = None,
        ):
        super().__init__(
            mongo_db_config,
            job_id,
            task_id,
            context_id,
            parent_context_id,
        )

    @new_task_id
    @ensure_context_id
    def get_date_wise_doc_count(self, collection_name: str) -> Optional[List]:
        """
        Get the dates and respective document counts, ordered by date.

        Returns
        -------
        list of tuple of (datetime.date, int) or None
            List of tuples containing (date, document count).
            Returns None if no documents are found.

        Raises
        ------
        CustomException
            If query execution fails.

        Examples
        --------
        >>> coleection_name = "test_raw_data"
        >>> counts = mongo_op.get_date_wise_doc_count(collection_name)
        >>> if counts:
        ...     for date, count in counts:
        ...         print(date, count)
        """
        start_time = time.perf_counter()
        try:
            collection = self._get_collection(collection_name)
            pipeline = [
                            {
                                "$group": {
                                    "_id": {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$published"
                                        }
                                    },
                                    "count": {"$sum": 1}
                                }
                            },
                            {
                                "$sort": {"_id": 1}
                            }
                        ]
            result = list(collection.aggregate(pipeline))
            date_wise_count = None
            if result:
                # Convert _id from string to datetime.date
                date_wise_count = [
                    (group['_id'], group['count'])
                    for group in result
                ]
                self.logging.debug(f"Fetched latest document: {date_wise_count}", start_time)
                return date_wise_count
            else:
                self.logging.info(f"No documents found : {date_wise_count}.", start_time)
                return date_wise_count
        except Exception as e:
            self.logging.error(f"Error fetching latest date: {e}", start_time)
            raise CustomException(e, sys)

    @new_task_id
    @ensure_context_id
    def is_article_link_exists(self, collection_name: str, article_link: str):
        """
        Check if a document with the given article link exists.

        Parameters
        ----------
        article_link : str
            URL of the article.

        Returns
        -------
        bool
            True if the document exists, False otherwise.

        Raises
        ------
        CustomException
            If query fails.

        Examples
        --------
        >>> exists = mongo_op.is_article_link_exists("http://example.com/article123")
        >>> print(exists)
        True
        """
        start_time = time.perf_counter()
        try:
            collection = self._get_collection(collection_name)
            doc_url = collection.find_one(
                filter={
                    self.config.MONGO_DOC_ARTICLE_URL_KEY: article_link,
                }
            )

            if doc_url is not None:
                self.logging.info(f"Document exists for Url: {article_link}", start_time)
                return True
            else:
                self.logging.info(f"No document exists for Url: {article_link}", start_time)
                return False
        except Exception as e:
            self.logging.error(f"Error while fetching data from MongoDB: {e}", start_time)
            raise CustomException(e, sys)
