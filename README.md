# COHERENT Migration

This repository records a learning-oriented reproduction and migration of
[MrKeee/COHERENT](https://github.com/MrKeee/COHERENT).

The codebase was imported from upstream commit
`17554a52792e302921bbb5e5fd3b4049e25b50d4`. Please refer to the upstream
repository for the original project description, paper, setup instructions,
and authorship information.

## Repository versions

- `main`: referenced upstream source snapshot, with this attribution README.
- `ubuntu20-ros1`: fixes verified during reproduction on Ubuntu 20.04 and ROS1
  Noetic.
- `ubuntu22-ros2`: ongoing migration to Ubuntu 22.04 and ROS2 Humble.

The detailed scope, compatibility constraints, excluded external data, and
migration sequence are documented in [MIGRATION.md](MIGRATION.md) on the
migration branches.

## Attribution

COHERENT and the bundled OmniGibson-derived source originate from their
respective upstream authors. This repository documents downstream changes and
does not claim ownership of the original work. Existing copyright and license
files are retained; downstream modifications are identified through Git
history.

Large simulator installations, datasets, robot assets, generated build trees,
credentials, and experiment logs are not distributed through this repository.
