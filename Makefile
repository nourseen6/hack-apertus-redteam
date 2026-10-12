.PHONY: run replay

# Official entry point. Judges run this from a clean checkout of the repository root.
run:
	$(MAKE) -C track_1a run

replay:
	$(MAKE) -C track_1a replay
