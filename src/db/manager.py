# Standard library imports
import sqlite3
from typing import Annotated, List, Tuple, Optional


class Database:
    """
    A class to interact with an SQLite database.

    This class provides methods to fetch data and insert data into a database.

    Parameters
    ----------
    db_path : str
        The path to the SQLite database file.

    Attributes
    ----------
    db_path : str
        The path to the SQLite database file.
    """

    def __init__(self, db_path: Annotated[str, "Path to the SQLite database"]):
        """
        Initializes the Database class with the provided database path.

        Parameters
        ----------
        db_path : str
            The path to the SQLite database file.
        """
        self.db_path = db_path

    def fetch(
            self,
            sql_file_path: Annotated[str, "Path to the SQL file"]
    ) -> Annotated[List[Tuple], "Results fetched from the query"]:
        """
        Executes a SELECT query from an SQL file and fetches the results.

        Parameters
        ----------
        sql_file_path : str
            Path to the SQL file containing the SELECT query.

        Returns
        -------
        List[Tuple]
            A list of tuples representing rows returned by the query.

        Examples
        --------
        >>> db = Database("example.db")
        >>> result = db.fetch("select_query.sql")
        >>> print(results)
        [(1, 'data1'), (2, 'data2')]
        """
        with open(sql_file_path, encoding='utf-8') as f:
            query = f.read()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return results

    def insert(
            self,
            sql_file_path: Annotated[str, "Path to the SQL file"],
            params: Optional[Annotated[Tuple, "Query parameters"]] = None
    ) -> Annotated[int, "ID of the last inserted row"]:
        """
        Executes an INSERT query from an SQL file and returns the last row ID.

        Parameters
        ----------
        sql_file_path : str
            Path to the SQL file containing the INSERT query.
        params : tuple, optional
            Parameters for the query. Defaults to None.

        Returns
        -------
        int
            The ID of the last inserted row.

        Examples
        --------
        >>> db = Database("example.db")
        >>> last_id_ = db.insert("insert_query.sql", ("value1", "value2"))
        >>> print(last_id)
        3
        """
        with open(sql_file_path, encoding='utf-8') as f:
            query = f.read()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

