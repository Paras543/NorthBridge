import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.core.ml.schemas import ClusterProfile,SegmentationResult,MLValidationError

MIN_ROWS_FOR_CLUSTERING = 10

def run_segmentation(df: pd.DataFrame, n_cluster: int = 3) -> SegmentationResult:

    numeric_df = df.select_dtypes(include="number").dropna()

    if numeric_df.shape[1]<2:
        raise MLValidationError(
            f"Only {numeric_df.shape[1]} numeric column(s) found; need at least 2 for clustering."
        )
    
    if len(numeric_df) < MIN_ROWS_FOR_CLUSTERING:
        raise MLValidationError(
            f"Only {len(numeric_df)} usable rows found; need at least {MIN_ROWS_FOR_CLUSTERING} to cluster."
        )
    
    effective_k = min(n_cluster,len(numeric_df)//3) or 1
    if effective_k <2:
        raise MLValidationError("Not enough rows to form more than one cluster.")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(numeric_df)
    
    model = KMeans(n_clusters=effective_k,random_state=42,n_init="auto")
    labels = model.fit_predict(scaled)
    numeric_df["_cluster"] = labels

    profiles = []
    overall_means = numeric_df.drop(columns="_cluster").mean()

    for cluster_id in sorted(numeric_df["_cluster"].unique()):
        subset = numeric_df[numeric_df["_cluster"] == cluster_id].drop(columns="_cluster")
        means = subset.mean()

        
        deviations = (means - overall_means) / overall_means.replace(0, 1)
        top_feature = deviations.abs().idxmax()
        direction = "higher" if deviations[top_feature] > 0 else "lower"

        profiles.append(
            ClusterProfile(
                cluster_id=int(cluster_id),
                size=len(subset),
                description=f"{direction} {top_feature} relative to average",
                representative_stats={k: round(v, 2) for k, v in means.items()},
            )
        )

    return SegmentationResult(n_clusters=effective_k, profiles=profiles)

    


