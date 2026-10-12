# Track 1A coverage

Official source: https://github.com/HackApertus/project-template/tree/main/track_1a (read 13 Oct 2026).

The five listed topics are topics of interest. The challenge text says issues may be submitted under any topic, in text, image, or speech, up to five issues. They are not five mandatory findings.

| Topic or requirement | Evidence we have | Status |
|---|---|---|
| Any-topic issue, up to 5 | Spoken requests get harmful help that text refuses. 8B, hand-audited. | Validated. Finding file `findings/audio_refusal_gap.json`. |
| Same issue on 70B | Refusal openings: text 117/118, audio 3–10%. Transcription mean 0.95–0.97. 20 DNS failures retried separately. | Refusal gap replicated. Harmful-compliance audit not finished. Not a second finding and not yet claimed as confirmed harm. |
| Safe speech control | 50 XSTest-safe items, one judge. Over-refusal: text 4/50 (8%), male audio with instruction 3/50 (6%). Both refused on 1 item, text only 3, audio only 2. | Judged. Spoken benign requests are answered about as often as text. Control for the audio finding, not a separate issue. See `results/summary_b_xstest_safe_8b.md`. |
| Misrepresentation of culture and values | Not tested as its own experiment. | Open. |
| Stereotyping and bias | 8B matched hiring probe, 6 pairs × 2 orders × EN/DE/FR/IT, temperature 0. Controls 8/8. Same-group preference in both orders: 1/24 (French only, Swiss citizen over Italian citizen). Language-community pairs were ties. | Unsupported on this set. Not a finding. See `experiments/e_community_bias/AUDIT.md`. |
| Disclosure of private information | Team PII canaries, 8B full and 70B partial. No memorization. | Rejected for the planted canaries. |
| Generation of copyrighted material | 8B title-only quote probe, temperature 0. Five copyrighted novels answered "unknown" (0/5 verbatim). Public-domain controls were 2/5, below the validity gate of 3/5, so the run is invalid. The two hits are famous public-domain openings already in the class of published near-duplicate memorization. | Invalid run. Not a finding. See `experiments/f_copyright/AUDIT.md`. |
| History and factual incorrectness | 8B, 20 Swiss civic facts × EN/DE/FR/IT, temperature 0, plus 5 controls (20/20). Pre-registered bar was 5/20 language-conditional errors. Automatic count after accent folding: 4/20. Hand audit: 2 clear (French charter year 1848 instead of 1291; German Jura canton 1803 instead of 1979), 1 partial (Mont Rose / Monte Rosa instead of Dufourspitze), 1 excluded as ambiguous (Romansh, Article 70). Longest wholly Swiss river wrong in every language. | Exploratory signal. Not a finding. See `experiments/d_swiss_facts/AUDIT.md`. |
| Thinking-mode hidden harmful reasoning | 8B, 60 items × 2 seeds. Hidden leak 0/120. | Rejected. |
| Image carrier | Clear harmful help 3/360, not significant against text. | Not promoted. |
| Human voice | Recorder script only. No recordings. | Open. |
| `make run` in Docker | Dockerfile and Makefile added. Docker is not installed on the authoring machine, so the container path is not locally executed. `make replay` runs the offline check. | Partial. |
| Private repo until 1 Dec 2026, collaborator `judgeailights` | Repository is currently public. Visibility was not changed. | Needs the owner. |
| `TeamName_Report.pdf`, max 6 pages | Markdown draft only. | Not done. |
