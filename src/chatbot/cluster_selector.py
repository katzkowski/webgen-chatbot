from typing import Optional, Tuple

from pandas.core.frame import DataFrame
from website_spec import WebsiteSpec


class ClusterSelector:
    """Selects the best-fitting cluster for a website specification."""

    def __init__(self, rankings: DataFrame) -> None:
        """Init a cluster selector instance.

        Args:
            rankings (DataFrame): dataframe containing label rankings for all clusters
        """
        self.rankings = rankings

    def get_cluster(self, spec: WebsiteSpec, type: str) -> Optional[int]:
        """Returns the best-matching cluster for a website spec depending on type.

        Args:
            spec (WebsiteSpec): website specification object
            type (str): match type: "CAT", "FEAT", "ALL"

        Returns:
            Optional[int]: cluster id, or None.
        """
        if type == "CAT":
            cat_rankings = None

            # get ranking for category
            if spec.cats:
                cats = list(map(lambda entity: (entity[1], entity[2]), spec.cats))

                cat_rankings = self.get_rankings(cats[0])
                return int(cat_rankings["cluster_id"].iloc[0])
        elif type == "FEAT":

            feat_rankings = None

            # get ranking for feature
            if spec.feats:
                feats = list(map(lambda entity: (entity[1], entity[2]), spec.feats))

                feat_rankings = self.get_rankings(feats[0])
                return int(feat_rankings["cluster_id"].iloc[0])

        elif type == "ALL":
            # extract cat rankings
            cat = list(map(lambda entity: (entity[1], entity[2]), spec.cats))[0]
            cat_rankings = (
                self.get_rankings(cat)
                .set_index("cluster_id")
                .sort_values(by=["factor_lf_ilf"], ascending=False)
                .rename(columns={"factor_lf_ilf": "factor_lf_ilf: CAT"})
            )

            # extract feat rankings
            feat = list(map(lambda entity: (entity[1], entity[2]), spec.feats))[0]
            feat_rankings = (
                self.get_rankings(feat)
                .set_index("cluster_id")
                .sort_values(by=["factor_lf_ilf"], ascending=False)
                .rename(columns={"factor_lf_ilf": "factor_lf_ilf: FEAT"})
            )

            # apply weights
            cat_weight = 0.75
            cat_rankings["factor_lf_ilf: CAT"] = (
                cat_rankings["factor_lf_ilf: CAT"] * cat_weight
            )

            feat_weight = 0.25
            feat_rankings["factor_lf_ilf: FEAT"] = (
                feat_rankings["factor_lf_ilf: FEAT"] * feat_weight
            )

            # join rankings to largee dataframe
            joined = DataFrame().join([cat_rankings, feat_rankings], how="outer")

            # sum all rows
            joined["score_sum"] = joined.sum(axis=1)
            best_df = joined.sort_values(by=["score_sum"], ascending=False)

            return int(best_df.index[0])

        return None

    def get_rankings(self, entity: Tuple[str, str]) -> DataFrame:
        """Returns a dataframe with cluster rankings for an entity sorted descendingly by factor-lf-ilf.

        Args:
            entity (Tuple[str, str]): list of entities: label, id

        Returns:
            DataFrame: dataframe with ranked cols [cluster_id, cluster_rank, label_name, factor_lf_ilf] for entity
        """
        return self.rankings[self.rankings["label_name"] == entity[1]].sort_values(
            by=["factor_lf_ilf"], ascending=False
        )[["cluster_id", "factor_lf_ilf"]]
