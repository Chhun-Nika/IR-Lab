# Information Retrieval Evaluation — Learning Notes

Source: `evaluation-slides.pdf` (27 slides), lecturer Mr. Natt KORAT, CADT.

## 1. Why evaluate search?

In Lab 3, TF-IDF ranked `d04` first for the query **python**, while BM25 ranked `d18` first. Looking at two lists by eye does not establish which ranking is better. Evaluation lets us compare retrieval-system choices—such as stemming rules and BM25 parameters `k1` and `b`—with evidence rather than guesses.

## 2. Test collections and relevance judgments

A test collection has three components:

1. A document collection.
2. Queries (or information needs).
3. Relevance judgments (**qrels**), which say whether each document satisfies a need.

Humans make qrels; they are not computed by the search system. For a query such as **python**, `d04` could be a useful introduction and `d18` a short code snippet, while `d05` is not relevant.

### Binary and graded relevance

- **Binary relevance:** relevant / not relevant.
- **Graded relevance:** how relevant a document is, often on a 0–3 scale.

Graded qrels preserve the important difference between a merely useful result and the best possible result, so they can reward a system that ranks the best document first.

Small projects may use the team or volunteers as judges. Large evaluations such as [TREC](https://trec.nist.gov/) use trained annotators and guidelines. Qrels are data, so they can contain uncertainty and noise.

## 3. Precision, recall, and F1

- **Precision:** among retrieved documents, what fraction is relevant?
- **Recall:** among all relevant documents, what fraction was retrieved?
- **F1:** the harmonic mean of precision and recall; it penalizes a system that is strong in only one of them.

\[
P = \frac{TP}{TP + FP}, \qquad
R = \frac{TP}{TP + FN}, \qquad
F1 = 2\frac{P R}{P + R}
\]

At a cutoff `k`, evaluate only the first `k` retrieved results:

\[
P@k = \frac{\text{relevant documents in top } k}{k}, \qquad
R@k = \frac{\text{relevant documents in top } k}{\text{all relevant documents}}
\]

`k` should match how far a typical user is likely to inspect. A ranking with two relevant documents in its top three, when there are two relevant documents total, has `P@3 = 2/3 = 0.67`, `R@3 = 2/2 = 1.00`, and `F1@3 = 0.80`. Changing `k` can change the result: in the same example, `P@1 = 1.00` but `R@1 = 0.50`.

## 4. Average Precision (AP) and MAP

A single cutoff can hide where relevant documents appear. **Average Precision** evaluates precision at every rank containing a relevant result, then averages these values:

\[
AP = \frac{1}{|R|}\sum_{i=1}^{N} P@i \cdot rel(i)
\]

where `rel(i)` is 1 at a relevant rank and 0 otherwise. Relevant documents earlier in the list contribute more to AP. For relevant documents at ranks 1 and 3, AP is `(1.00 + 0.67) / 2 = 0.83`.

**Mean Average Precision (MAP)** is AP averaged across all queries:

\[
MAP = \frac{1}{|Q|}\sum_{q \in Q} AP_q
\]

AP and MAP use binary relevance. They cannot distinguish two rankings that contain the same relevant documents at the same ranks but reverse their quality: `d04` (very relevant) then `d18` (somewhat relevant), versus `d18` then `d04`, can both receive `AP = 1.00`.

## 5. NDCG: graded relevance and rank position

**Normalized Discounted Cumulative Gain (NDCG)** addresses AP/MAP's limitation by combining:

- **Graded gain:** a high relevance grade earns much more credit.
- **Rank discount:** the same document earns less credit at lower ranks.
- **Normalization:** score against the ideal ordering for that query.

For a relevance grade `r`, the gain is `2^r - 1`:

| Grade | Meaning | Gain |
| --- | --- | ---: |
| 0 | Not relevant | 0 |
| 1 | Somewhat relevant | 1 |
| 2 | Useful | 3 |
| 3 | Highly relevant | 7 |

\[
DCG@k = \sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)}
\]

\[
NDCG@k = \frac{DCG@k}{IDCG@k}
\]

`IDCG@k` is the DCG of the ideal ranking—grades sorted from highest to lowest—so NDCG ranges from 0 to 1. In the worked example, ranking grade 1 before grade 3 gives `DCG@3 = 5.43`; the ideal order gives `IDCG@3 = 7.63`; therefore `NDCG@3 = 0.71`. The ideal ranking scores `1.00`.

## 6. Choosing a metric

| Retrieval goal | Useful metric |
| --- | --- |
| Show a few good results immediately | `P@k`, `NDCG@k` |
| Find as many relevant documents as possible | Recall / `R@k` |
| Compare binary-ranked systems across queries | MAP |
| Reward highly relevant results near the top | NDCG |

## 7. Annotator disagreement

People can reasonably disagree about borderline documents. Different qrels change MAP and NDCG, so a tiny difference between systems may not be meaningful. Use clear grading guidelines, example cases, repeated judgments, and discuss disagreements before making claims.

## 8. Core recap

- A test collection is **documents + queries + relevance judgments**.
- `P@k`, `R@k`, and `F1@k` measure effectiveness at one cutoff.
- AP rewards early relevant documents; MAP averages AP across queries.
- NDCG uses graded relevance and discounts low-ranked results.
- The metric must fit the search goal, and conclusions depend on trustworthy qrels.
