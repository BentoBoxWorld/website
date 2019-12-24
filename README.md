# Webtool
Webtool for BentoBox that allows users to create a ready to use .zip file with all desired addons in it.

The webtool fetches all addons from the official bentobox repository, which is located at [codemc](https://repo.codemc.io/service/rest/repository/browse/maven-releases/world/bentobox/).

[download.bentobox.world](https://download.bentobox.world)

## Adding an addon from codemc
You might add new addons from codemc by creating a pull request for the following changes:

1. Add your addon name to the bottom of the `addons.txt` file
   - Keep in mind that addon names are **case-sensitive**, so it must match the parent folder name on [codemc](https://repo.codemc.io/service/rest/repository/browse/maven-releases/world/bentobox/).
2. Create a markdown description file using the same name as above in `/teplates/descriptions/` with `.md` as file extension.

