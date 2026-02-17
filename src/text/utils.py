# Standard library imports
from typing import Annotated, Dict, Any, List


class Annotator:
    """
    A class to annotate a structured sentiment model (SSM) with various
    attributes such as sentiment, profanity, summary, and conflict.

    Parameters
    ----------
    ssm : list of dict
        A list of dictionaries representing the structured sentiment model.

    Attributes
    ----------
    ssm : list of dict
        The structured sentiment model to be annotated.
    global_summary : str
        The global summary of the annotations.
    global_conflict : bool
        The global conflict status of the annotations.
    """

    def __init__(self, ssm: Annotated[List[Dict[str, Any]], "Structured Sentiment Model"]):
        """
        Initializes the Annotator class with the provided SSM.

        Parameters
        ----------
        ssm : list of dict
            A list of dictionaries representing the structured sentiment model.
        """
        self.ssm = ssm
        self.global_summary = ""
        self.global_conflict = False

    def add_sentiment(
            self,
            sentiment_results: Annotated[Any, "Sentiment analysis results: dict with 'sentiments' key or list of {index, sentiment}"]
    ):
        """
        Adds sentiment data to the SSM. Accepts either {"sentiments": [...]} or a raw list.
        Handles out-of-range indices by applying in-range ones; if all indices are wrong,
        assigns by position (first item -> index 0, etc.).
        """
        # Normalize: accept raw list (LLM sometimes returns array instead of object)
        if isinstance(sentiment_results, list):
            sentiments_list = sentiment_results
        elif sentiment_results and isinstance(sentiment_results, dict) and "sentiments" in sentiment_results:
            sentiments_list = sentiment_results["sentiments"]
        else:
            print("Warning: 'sentiments' key is missing in sentiment_results. Defaulting to Neutral.")
            for item in self.ssm:
                item.setdefault("sentiment", "Neutral")
            return

        if not isinstance(sentiments_list, list):
            for item in self.ssm:
                item.setdefault("sentiment", "Neutral")
            return

        n = len(self.ssm)
        # Ensure each item has "index" and "sentiment"
        valid_entries = []
        for entry in sentiments_list:
            if not isinstance(entry, dict) or "sentiment" not in entry:
                continue
            idx = entry.get("index", -1)
            sent = entry.get("sentiment", "Neutral")
            if sent not in ("Positive", "Negative", "Neutral"):
                sent = "Neutral"
            valid_entries.append((idx, sent))

        # Check if any index is in range; if not, assign by position
        any_in_range = any(0 <= idx < n for idx, _ in valid_entries)
        if not any_in_range and len(valid_entries) <= n:
            # LLM returned wrong indices (e.g. word indices); use order: first -> 0, second -> 1, ...
            valid_entries = [(i, sent) for i, (_, sent) in enumerate(valid_entries)]

        for idx, sent in valid_entries:
            if 0 <= idx < n:
                self.ssm[idx]["sentiment"] = sent
            elif idx >= n:
                pass  # skip out-of-range

        for item in self.ssm:
            item.setdefault("sentiment", "Neutral")

    def add_profanity(
            self,
            profane_results: Annotated[Dict[str, Any], "Profanity detection results"]
    ) -> List[Dict[str, Any]]:
        """
        Adds profanity data to the SSM.

        Parameters
        ----------
        profane_results : dict
            A dictionary containing profanity detection results, including
            a "profanity" key with a list of profanity dictionaries.

        Returns
        -------
        list of dict
            The updated SSM with profanity annotations.

        Examples
        --------
        >>> annotator = Annotator([{"text": "example"}])
        >>> results = {"profanity": [{"index": 0, "profane": True}]}
        >>> annotator.add_profanity(profane_results)
        """
        if not profane_results or "profanity" not in profane_results:
            print("Warning: 'profanity' key is missing in profane_results. Defaulting to False.")
            for item in self.ssm:
                item.setdefault("profane", False)
            return self.ssm

        if len(profane_results["profanity"]) != len(self.ssm):
            print(f"Mismatch: SSM Length = {len(self.ssm)}, "
                  f"Profanity Length = {len(profane_results['profanity'])}")
            print("Adjusting to match lengths...")

        if len(profane_results["profanity"]) < len(self.ssm):
            for idx in range(len(profane_results["profanity"]), len(self.ssm)):
                profane_results["profanity"].append({"index": idx, "profane": False})

        elif len(profane_results["profanity"]) > len(self.ssm):
            profane_results["profanity"] = profane_results["profanity"][:len(self.ssm)]

        for profanity_data in profane_results["profanity"]:
            idx = profanity_data["index"]
            if idx < len(self.ssm):
                self.ssm[idx]["profane"] = profanity_data["profane"]
            else:
                print(f"Skipping profanity data at index {idx}, out of range.")

        return self.ssm

    def add_summary(
            self,
            summary_result: Annotated[Dict[str, str], "Summary results"]
    ) -> Dict[str, Any]:
        """
        Adds a global summary to the annotations.

        Parameters
        ----------
        summary_result : dict
            A dictionary containing a "summary" key with the summary text.

        Returns
        -------
        dict
            The updated SSM and global summary.

        Examples
        --------
        >>> annotator = Annotator([{"text": "example"}])
        >>> result = {"summary": "This is a summary."}
        >>> annotator.add_summary(summary_result)
        """
        if not summary_result or "summary" not in summary_result:
            print("Warning: 'summary' key is missing in summary_result.")
            return {"ssm": self.ssm, "summary": self.global_summary}

        self.global_summary = summary_result["summary"]
        return {"ssm": self.ssm, "summary": self.global_summary}

    def add_conflict(
            self,
            conflict_result: Annotated[Dict[str, bool], "Conflict detection results"]
    ) -> Dict[str, Any]:
        """
        Adds a global conflict status to the annotations.

        Parameters
        ----------
        conflict_result : dict
            A dictionary containing a "conflict" key with a boolean value.

        Returns
        -------
        dict
            The updated SSM and global conflict status.

        Examples
        --------
        >>> annotator = Annotator([{"text": "example"}])
        >>> result = {"conflict": True}
        >>> annotator.add_conflict(conflict_result)
        """
        if not conflict_result or "conflict" not in conflict_result:
            print("Warning: 'conflict' key is missing in conflict_result.")
            return {"ssm": self.ssm, "conflict": self.global_conflict}

        self.global_conflict = conflict_result["conflict"]
        return {"ssm": self.ssm, "conflict": self.global_conflict}

    def finalize(self) -> Dict[str, Any]:
        """
        Finalizes the annotations by returning the updated SSM along with
        global annotations for summary, conflict, and topic.

        Returns
        -------
        dict
            A dictionary containing the updated SSM and global annotations.

        Examples
        --------
        >>> annotator = Annotator([{"text": "example"}])
        >>> annotator.finalize()
        {'ssm': [{'text': 'example'}], 'summary': '', 'conflict': False}
        """
        for item in self.ssm:
            item.setdefault("sentiment", "Neutral")
            item.setdefault("profane", False)

        return {
            "ssm": self.ssm,
            "summary": self.global_summary,
            "conflict": self.global_conflict
        }
