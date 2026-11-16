"""Manifest validation and deterministic deployment configuration generation."""
from pathlib import Path
import json
import re
import tomllib
from microduck_hosting import validate_profile, document_lines, site_lines

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'sites.toml'
DOMAIN_RE = re.compile(r'(?=.{1,190}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$')
SLUG_RE = re.compile(r'[a-z][a-z0-9-]{0,24}$')

# Exact public paths and hashes from the pinned candidate manifest; no wildcard file serving.
OPFS_PUBLIC_FILES = {'/assets/desktop/apps.json': '2b835e478b1a5e24015b7a353b32838e6026d7fe6f56bad71660f6f7ce83f07a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/index.css': 'e3b9183dff2c77cbeb6fd7b7ae2775c3ebaa4b9acb888514efc1278d8227a469', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/index.mjs': '684bfe19edaf7cce3de3986c87d95cd1e05f6b4b76976218359934137d6d17cb', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/index.mjs.LEGAL.txt': '94a6c30bde6b35e74c6c13013c8029bc7e810ba1d7e86726f67cf4bbd8fc1011', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@babel-runtime-7.29.10/LICENSE.txt': '117da2af0d4ce0fe1c8e19b5cff9dcd806adf973d328d27b11d4448c4ff24f76', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-cache-11.14.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-css-11.13.5/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-hash-0.9.2/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-is-prop-valid-1.4.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-memoize-0.9.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-react-11.14.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-serialize-1.3.3/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-sheet-1.4.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-styled-11.14.1/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-unitless-0.10.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-use-insertion-effect-with-fallbacks-1.2.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-utils-1.4.2/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@emotion-weak-memoize-0.4.0/LICENSE.txt': '6e8d23763cf7cb707ad8f6677aa502ebeca1dda447e6d6e57f6549c1625b9c4a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@formatjs-fast-memoize-3.1.7/LICENSE.md.txt': 'b1cc980e28e9e48f377db191578a9361494ca7117185b69dd66cabaf5b460fb7', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@formatjs-icu-messageformat-parser-3.5.18/LICENSE.md.txt': 'b1cc980e28e9e48f377db191578a9361494ca7117185b69dd66cabaf5b460fb7', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@formatjs-icu-skeleton-parser-2.1.11/LICENSE.md.txt': 'b1cc980e28e9e48f377db191578a9361494ca7117185b69dd66cabaf5b460fb7', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@formatjs-intl-4.2.1/LICENSE.md.txt': 'b1cc980e28e9e48f377db191578a9361494ca7117185b69dd66cabaf5b460fb7', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@fortawesome-fontawesome-svg-core-7.3.1/LICENSE.txt.txt': '20c6f40715a567c97b80f6944beb8bb325835cab47ea7dcab89ee3b8e077eced', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@fortawesome-free-brands-svg-icons-7.3.1/LICENSE.txt.txt': '20c6f40715a567c97b80f6944beb8bb325835cab47ea7dcab89ee3b8e077eced', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@fortawesome-free-solid-svg-icons-7.3.1/LICENSE.txt.txt': '20c6f40715a567c97b80f6944beb8bb325835cab47ea7dcab89ee3b8e077eced', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@fortawesome-react-fontawesome-3.5.0/LICENSE.txt.txt': 'aaeca2af41f9d13e49205099914902115ca197cdae49f7d2b31bc5d6aa2bbd83', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@mui-material-9.5.0/LICENSE.txt': '4c57cedbef546270e5648786682f633b2e6ae62c8862a45797bcb6d0bffda98d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@mui-private-theming-9.5.0/LICENSE.txt': '4c57cedbef546270e5648786682f633b2e6ae62c8862a45797bcb6d0bffda98d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@mui-styled-engine-9.5.0/LICENSE.txt': '4c57cedbef546270e5648786682f633b2e6ae62c8862a45797bcb6d0bffda98d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@mui-system-9.5.0/LICENSE.txt': '4c57cedbef546270e5648786682f633b2e6ae62c8862a45797bcb6d0bffda98d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@mui-utils-9.5.0/LICENSE.txt': '4c57cedbef546270e5648786682f633b2e6ae62c8862a45797bcb6d0bffda98d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@popperjs-core-2.11.8/LICENSE.md.txt': 'bf67e2c9b7974543bb18ced3a0b37f53729aaff953b442dd89a3adaf90fd93e8', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@react-dnd-asap-5.0.2/LICENSE.md.txt': '39c7589834a86c769cbd03a802bc8a1cfcdd8cf9eabb9ce53b7532db15d0e9d9', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@react-dnd-invariant-4.0.2/LICENSE.txt': '10c8da64ecfa3067cf9231e0ba19b8d7730e7fed3ac5eaa37ccb97c3c5e71336', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@react-dnd-invariant-4.0.2/provenance.json': 'd93e5f57e620bc25afd5a50fbf307ed7282dca67b040f1e25222e046fcd4ba46', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@react-dnd-shallowequal-4.0.2/LICENSE.txt': '10c8da64ecfa3067cf9231e0ba19b8d7730e7fed3ac5eaa37ccb97c3c5e71336', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@react-dnd-shallowequal-4.0.2/provenance.json': 'd93e5f57e620bc25afd5a50fbf307ed7282dca67b040f1e25222e046fcd4ba46', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@reduxjs-toolkit-2.13.0/LICENSE.txt': '49784961ec6c4941437b7a2c54d8977d0528076a9e7c73dd40f7d0942b8f106d', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@samuelncui-chonky-0.3.10/LICENSE.txt': '1d5b9db1a5d668cf0a03eb689d9b546e2e7a8e663f720f2384578a395b633085', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/@samuelncui-chonky-icon-fontawesome-0.3.10/LICENSE.txt': '1d5b9db1a5d668cf0a03eb689d9b546e2e7a8e663f720f2384578a395b633085', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/classnames-2.5.1/LICENSE.txt': '0c1c24dcc129cb0c02ee9803cfa7a50061c236a3b59b36a714c27f3ade66d7be', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/clsx-2.1.1/license.txt': '9a9edad7baae52622bddf3c15b2ef8a33d2c89f2d25408ad13e8a7481c6b0c97', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/deepmerge-4.3.1/license.txt.txt': '6cfc4687cb2f2d86f4a77e6b526290d3878e5e512f3fec2f4cb36a9cb36f798b', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/dnd-core-16.0.1/LICENSE.txt': '65a1f00f35ea469048896fbfec3c5faed7d3fe7c7e0be2a0478470b59d9e1439', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/exact-trie-1.0.13/LICENSE.txt': 'b99e1265e92516d0806249ec1ca0c8e2f52ecf8073e786cbf94b105de91bdbb9', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/fast-deep-equal-3.1.3/LICENSE.txt': '7bf9b2de73a6b356761c948d0e9eeb4be6c1270bd04c79cd489c1e400ffdfc1a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/fast-sort-3.4.1/LICENSE.txt': 'b81d5b61bb4d61635811ce0062fcdddf2fec0408a462715bffdf627003ba54b7', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/filesize-11.0.29/LICENSE.txt': 'dcc6ac957d32319cb726f06418d34d6d7d3405b4c8a19eea9a2b9ffbced07867', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/fuzzy-search-3.3.0/LICENSE.md.txt': 'da35ef625a0b2fc3e910f0f6f243464a99ec4ca92b5e7c1948c24b8bc5301b8c', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/hoist-non-react-statics-3.3.2/LICENSE.md.txt': 'eb32ff0ec52b6ea86e3d3e06c6ad1b68ee03798b6729af13919f6d5c14b368f3', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/hotkeys-js-3.13.15/LICENSE.txt': 'efc6759044c0b3c95f5ccc9b09a6aa325cded29355eb65b45243e881f0c9d36b', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/immer-11.2.9/LICENSE.txt': '99cf22f6960a6fe228ec84ea9aefb0d75b27999ece83a3a9801e1c2081fa270b', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/intl-messageformat-11.2.15/LICENSE.md.txt': 'cc4143615b27c66eafbe913f132a9e41ac14c1e2ec6b2df24dafeaa97f028850', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/object-assign-4.1.1/license.txt': '6fb9754611c20f6649f68805e8c990e83261f29316e29de9e6cedae607b8634c', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/prop-types-15.8.1/LICENSE.txt': 'f657f99d3fb9647db92628e96007aabb46e5f04f33e49999075aab8e250ca7ce', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-19.2.0/LICENSE.txt': 'da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-dnd-16.0.1/LICENSE.txt': '720a9b51db3dc48d2afd62039f019614179b18d0fe9456bd2c6ea41041e942dd', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-dnd-html5-backend-16.0.1/LICENSE.txt': '65a1f00f35ea469048896fbfec3c5faed7d3fe7c7e0be2a0478470b59d9e1439', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-dom-19.2.0/LICENSE.txt': 'da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-intl-10.2.2/LICENSE.md.txt': 'ef3171f69fb1c12e0f61968b478e6640b786dd2fdf7868cf2052d084b71aa92a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-is-16.13.1/LICENSE.txt': '52412d7bc7ce4157ea628bbaacb8829e0a9cb3c58f57f99176126bc8cf2bfc85', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-is-19.3.1/LICENSE.txt': 'da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-redux-9.3.1/LICENSE.md.txt': 'f2da73c752c6b87624755edacf927cbd915fa76555d383e74494bad4a5155ab3', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-transition-group-4.4.5/LICENSE.txt': 'b9adc17ad75a847d8743be2843935f0842a0ea4f45e7b0c7e17ed0be98614b9b', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/react-virtuoso-4.18.20/LICENSE.txt': '0c53d51ef7f29a43470f7c3132faf161fb72ea3b99ffa9e928981cd8681be6b8', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/redux-4.2.1/LICENSE.md.txt': 'f2da73c752c6b87624755edacf927cbd915fa76555d383e74494bad4a5155ab3', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/redux-5.0.1/LICENSE.md.txt': 'f2da73c752c6b87624755edacf927cbd915fa76555d383e74494bad4a5155ab3', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/redux-thunk-3.1.0/LICENSE.md.txt': '635da794c92d278f8355428be0f9922d643f556d4f75f33fe4aca6b98d27affe', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/reselect-5.3.0/LICENSE.txt': 'e98047a5dee068b33f82e8c4b7a63037b5108c93393198efd4097753004af5dd', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/scheduler-0.27.0/LICENSE.txt': 'da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/stylis-4.2.0/LICENSE.txt': '88c579c6ee44b41137a21321190d177982e5b17d4fa1b83a4a2e3ea325a8fc9a', '/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/licenses/use-sync-external-store-1.7.0/LICENSE.txt': 'da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93', '/assets/desktop/cache-manifest.json': '3c5d5a241231cb83eb62f71c7cb4ae632f3fa916b1892035cd68ee83a1a748d2', '/assets/desktop/offline-worker.js': 'd2c23435beac5ae0c354ee16eba9d708a975855e3538a4e36717b2900c9e2519', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/account-context.mjs': 'dd19562a1a13e2ac79142b9cb7a2cf0a3cba77ff03fa5407c0ced4e5c6a518e9', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/mirror.mjs': '67962be43d99bd0bb22229fc8f30c309d0637f9440e9903c2a070b6d618fa187', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/opfs/LICENSE.txt': '2153bd2978793748fbe0eb8f838ae2ae19f03f9d4ee5473dd1628a0c0790e4ab', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/opfs/core.mjs': '90b245475d95570135d4eba2b92717ac90350944e9ee7a5e6d595e275ebd5299', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/opfs/shared.mjs': '7399a7fe440c202f1d645230654aa86c035ac4adf072452ac718cc44efb44d9d', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/opfs/store.mjs': '65a74ef7439d530d766595834f70334bcfbe01d3fb31a9d906948a88cb334faf', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/opfs/worker.mjs': '9d97301fb4e9e20173bc0c2f57aa2e23c479b5dac0b2b193b76d0716fef7ca1e', '/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/verified-content.mjs': '4503fade5803896a036430cba092ec5c90c15ba6cd0d1028c7b4fd0503eccc12'}

def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported manifest schema')
    if 'codi_shared_ingress' in data and type(data['codi_shared_ingress']) is not bool:
        raise ValueError('codi_shared_ingress must be boolean')
    if data.get('codi_shared_ingress') and not any(s['domain']=='ksu.codes' and s['enabled'] and s.get('codi_preview') and s.get('codi_turn_certificate') for s in data['sites']):
        raise ValueError('Shared ingress requires the enabled KSU preview/certificate profile')
    if 'codi_beta_maintenance' in data and (type(data['codi_beta_maintenance']) is not bool or not data.get('codi_beta_simplified')):raise ValueError('Invalid beta maintenance gate')
    if 'codi_beta_opfs' in data:
        if data['codi_beta_opfs']!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or not data.get('codi_beta_simplified') or not data.get('codi_beta_active_overlay'):raise ValueError('Exact beta OPFS candidate and retained guarded baseline required')
    retained=data.get('codi_beta_retained_overlays',[]);active=data.get('codi_beta_active_overlay')
    if not isinstance(retained,list) or len(retained)>32 or any(not isinstance(x,str) or not re.fullmatch(r'[0-9a-f]{64}:[0-9a-f]{64}:[0-9a-f]{64}',x) for x in retained):raise ValueError('Invalid beta overlay records')
    pieces=[x.split(':') for x in retained]
    if len({x[0] for x in pieces})!=len(pieces) or len({x[2] for x in pieces})!=len(pieces):raise ValueError('Duplicate beta overlay')
    if active is not None and (not isinstance(active,str) or active not in [x[0] for x in pieces]):raise ValueError('Active overlay must be retained')
    if retained and active is None:raise ValueError('Retained beta overlays require an active guarded loader')
    if (retained or active is not None) and not data.get('codi_beta_simplified'):raise ValueError('Overlay requires beta site')
    beta=data.get('codi_beta_simplified')
    if beta is not None:
        if not isinstance(beta,str) or not re.fullmatch('[0-9a-f]{64}',beta):raise ValueError('Beta requires an exact desktop release hash')
        if any(site.get('domain')=='beta.ksu.codes' for site in data['sites']):raise ValueError('Beta hostname must not alias another site')
        if not data.get('codi_shared_ingress'):raise ValueError('Beta requires the managed shared ingress profile')
    seen = {k: set() for k in ['domain', 'slug', 'port', 'service', 'user']}
    for s in data['sites']:
        if not DOMAIN_RE.fullmatch(s['domain']) or not SLUG_RE.fullmatch(s['slug']):
            raise ValueError('Invalid domain or slug')
        if s['service'] != f"web-{s['slug']}.service" or s['user'] != f"site-{s['slug']}":
            raise ValueError('Service/account must match the validated slug')
        if type(s['port']) is not int or not 8011 <= s['port'] <= 8999:
            raise ValueError('Application port must be in 8011..8999')
        if type(s['workers']) is not int or not 1 <= s['workers'] <= 4:
            raise ValueError('Workers must be in 1..4; measure before increasing')
        if type(s['enabled']) is not bool:
            raise ValueError('enabled must be boolean')
        if 'codi_files' in s and (type(s['codi_files']) is not bool or s['domain']!='ksu.codes' or s['codi_files'] and (not s['enabled'] or not s.get('codi_preview',False))):
            raise ValueError('codi_files requires a boolean on enabled KSU preview only')
        if 'codi_rooms' in s and (type(s['codi_rooms']) is not bool or s['domain']!='ksu.codes' or s['codi_rooms'] and (not s['enabled'] or not s.get('codi_preview',False))):
            raise ValueError('codi_rooms requires a boolean on enabled KSU desktop only')
        if 'codi_chat_disabled' in s and (type(s['codi_chat_disabled']) is not bool or s['domain']!='ksu.codes' or not s.get('codi_preview')):
            raise ValueError('codi_chat_disabled requires a boolean on KSU desktop only')
        if 'codi_p2p_steward' in s and (type(s['codi_p2p_steward']) is not bool or s['domain']!='ksu.codes' or not s.get('codi_preview')):
            raise ValueError('codi_p2p_steward requires a boolean on KSU desktop only')
        if 'codi_official' in s and (type(s['codi_official']) is not bool or s['domain']!='ksu.codes' or s['codi_official'] and (not s['enabled'] or not s.get('codi_preview'))):
            raise ValueError('codi_official requires a boolean on enabled KSU preview only')
        if 'codi_readers' in s and (type(s['codi_readers']) is not str or s['codi_readers'] not in ('prepare','active') or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview') or not s.get('codi_rooms')):
            raise ValueError('codi_readers requires prepare/active on enabled KSU hosted rooms only')
        if 'codi_speech' in s and (not isinstance(s['codi_speech'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_speech']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_speech requires a SHA256 on enabled KSU preview only')
        if 'codi_frontend' in s and (not isinstance(s['codi_frontend'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_frontend']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_frontend requires a SHA256 on enabled KSU preview only')
        validate_profile(s)
        if 'codi_simplified' in s and (not isinstance(s['codi_simplified'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_simplified']) or s['domain']!='ksu.codes' or not s['enabled'] or s.get('codi_mount')!=''):
            raise ValueError('Simplified release requires root KSU desktop')
        for flag in ('codi_browser_relay','codi_large_files','codi_login_filter','codi_browser_sources'):
            if flag in s and (type(s[flag]) is not bool or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_simplified') or s.get('codi_simplified_mode')!='active'):
                raise ValueError(flag+' requires the active KSU Simplified site')
        if 'codi_simplified_mode' in s and (s['codi_simplified_mode'] not in ('preview','active') or not s.get('codi_simplified')):
            raise ValueError('Simplified mode requires a release')
        if 'codi_turn_certificate' in s and (type(s['codi_turn_certificate']) is not bool or s['domain']!='ksu.codes' or s['codi_turn_certificate'] and not s['enabled']):
            raise ValueError('codi_turn_certificate must be boolean on enabled ksu.codes only')
        if 'codi_preview' in s and (type(s['codi_preview']) is not bool or s['domain']!='ksu.codes'):
            raise ValueError('codi_preview must be a boolean on ksu.codes only')
        if 'codi_mount' in s and (type(s['codi_mount']) is not str or s['codi_mount'] not in ('','/hidden') or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_mount requires root or /hidden on the enabled KSU desktop only')
        if s.get('codi_mount','/hidden')=='' and s.get('codi_frontend'):
            raise ValueError('Root desktop requires its coherent native asset graph')
        if 'hardware_studio' in s and (type(s['hardware_studio']) is not bool or s['domain'] != 'hardware.ksu.codes'):
            raise ValueError('hardware_studio must be boolean on its exact hostname')
        if 'cardboard_studio' in s and (type(s['cardboard_studio']) is not bool or s['domain'] != 'cardboard.ksu.codes'):
            raise ValueError('cardboard_studio must be a boolean on its exact hostname')
        for k in seen:
            if s[k] in seen[k]:
                raise ValueError(f'Duplicate {k}: {s[k]}')
            seen[k].add(s[k])
    return data

def load(path=MANIFEST):
    return validate(tomllib.loads(path.read_text()))

def validate_beta_overlay_transition(old,new):
    """Preserve guarded loaders and retained URLs; not a host installer."""
    validate(old);validate(new)
    ignored={'codi_beta_active_overlay','codi_beta_retained_overlays','codi_beta_maintenance','codi_beta_opfs'}
    if {k:v for k,v in old.items() if k not in ignored}!={k:v for k,v in new.items() if k not in ignored}:raise ValueError('Only beta overlay fields may change')
    if not set(old.get('codi_beta_retained_overlays',[]))<=set(new.get('codi_beta_retained_overlays',[])):raise ValueError('Retained overlay assets must remain available')
    if old.get('codi_beta_active_overlay') and not new.get('codi_beta_active_overlay'):raise ValueError('Guarded beta loader cannot be removed')
    if old.get('codi_beta_opfs') and old.get('codi_beta_opfs')!=new.get('codi_beta_opfs'):raise ValueError('OPFS candidate cannot be removed')
    return True

def beta_overlay_routes(data):
    records=[x.split(':') for x in data.get('codi_beta_retained_overlays',[])]
    result=[];active=data.get('codi_beta_active_overlay')
    for index,(manifest,desktop,mirror) in enumerate(records):
        root='/srv/codi-connected/beta-overlays/'+manifest
        # Retained, content-addressed mirror routes survive loader rollback.
        result += [f'\t@beta_mirror_{index} path /storage/browser/mirror.{mirror}.mjs',f'\thandle @beta_mirror_{index} {{',f'\t\troot * {root}','\t\tfile_server','\t}',f'\t@beta_desktop_{index} path /assets/desktop/desktop-apps.{desktop}.js',f'\thandle @beta_desktop_{index} {{',f'\t\troot * {root}','\t\tfile_server','\t}']
        if manifest==active and not data.get('codi_beta_opfs'):
            result += ['\t@beta_overlay_loader {','\t\tpath /desktop-apps.js','\t\texpression `{http.request.uri.query} == "simplified=1"`','\t}','\thandle @beta_overlay_loader {',f'\t\trewrite * /assets/desktop/desktop-apps.{desktop}.js',f'\t\troot * {root}','\t\tfile_server','\t}']
    if data.get('codi_beta_opfs'):
        root='/srv/data/codi-beta-opfs/'+data['codi_beta_opfs']
        bundle='12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244'
        graph='0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a'
        for name,target in (('app','shell/app.js'),('desktop','shell/desktop-apps.js')):
            path='/app.js' if name=='app' else '/desktop-apps.js'
            result += [f'\t@beta_opfs_{name} {{',f'\t\tpath {path}','\t\texpression `{http.request.uri.query} == "simplified=1"`','\t}',f'\thandle @beta_opfs_{name} {{',f'\t\trewrite * /{target}',f'\t\troot * {root}','\t\tfile_server','\t}']
        result += ['\t@beta_opfs_files path '+' '.join(OPFS_PUBLIC_FILES),'\thandle @beta_opfs_files {',f'\t\troot * {root}','\t\tfile_server','\t}',f'\t@beta_opfs_unknown path /assets/desktop/apps/files/{bundle}/* /storage/browser/releases/{graph}/*','\thandle @beta_opfs_unknown {','\t\trespond "Not found" 404','\t}']
    return result

def dump(data):
    validate(data)
    lines = ['schema_version = 1', *(['codi_shared_ingress = '+str(data['codi_shared_ingress']).lower()] if 'codi_shared_ingress' in data else []), *(['codi_beta_simplified = '+json.dumps(data['codi_beta_simplified'])] if 'codi_beta_simplified' in data else []), *(['codi_beta_maintenance = '+str(data['codi_beta_maintenance']).lower()] if 'codi_beta_maintenance' in data else []), *(['codi_beta_opfs = '+json.dumps(data['codi_beta_opfs'])] if 'codi_beta_opfs' in data else []), *(['codi_beta_active_overlay = '+json.dumps(data['codi_beta_active_overlay'])] if 'codi_beta_active_overlay' in data else []), *(['codi_beta_retained_overlays = '+json.dumps(data['codi_beta_retained_overlays'])] if 'codi_beta_retained_overlays' in data else []), '']
    for s in data['sites']:
        lines.append('[[sites]]')
        for key in ['domain','slug','port','service','user','workers','enabled','theme','description','accent']:
            v = s[key]
            text = str(v).lower() if isinstance(v, bool) else str(v) if isinstance(v, int) else json.dumps(v, ensure_ascii=False)
            lines.append(f'{key} = {text}')
        if 'codi_preview' in s: lines.append('codi_preview = '+str(s['codi_preview']).lower())
        if 'codi_mount' in s: lines.append('codi_mount = '+json.dumps(s['codi_mount']))
        if 'codi_files' in s: lines.append('codi_files = '+str(s['codi_files']).lower())
        if 'codi_rooms' in s: lines.append('codi_rooms = '+str(s['codi_rooms']).lower())
        if 'codi_chat_disabled' in s: lines.append('codi_chat_disabled = '+str(s['codi_chat_disabled']).lower())
        if 'codi_p2p_steward' in s: lines.append('codi_p2p_steward = '+str(s['codi_p2p_steward']).lower())
        if 'codi_official' in s: lines.append('codi_official = '+str(s['codi_official']).lower())
        if 'codi_readers' in s: lines.append('codi_readers = '+json.dumps(s['codi_readers']))
        if 'codi_frontend' in s: lines.append('codi_frontend = '+json.dumps(s['codi_frontend']))
        if 'codi_speech' in s: lines.append('codi_speech = '+json.dumps(s['codi_speech']))
        if 'codi_simplified' in s: lines.append('codi_simplified = '+json.dumps(s['codi_simplified']))
        if 'codi_simplified_mode' in s: lines.append('codi_simplified_mode = '+json.dumps(s['codi_simplified_mode']))
        if 'codi_microduck_runner' in s: lines.append('codi_microduck_runner = '+json.dumps(s['codi_microduck_runner']))
        for flag in ('codi_browser_relay','codi_large_files','codi_login_filter','codi_browser_sources'):
            if flag in s: lines.append(flag+' = '+str(s[flag]).lower())
        if 'codi_turn_certificate' in s: lines.append('codi_turn_certificate = '+str(s['codi_turn_certificate']).lower())
        if 'hardware_studio' in s: lines.append('hardware_studio = '+str(s['hardware_studio']).lower())
        if 'cardboard_studio' in s: lines.append('cardboard_studio = '+str(s['cardboard_studio']).lower())
        lines.append('')
    return '\n'.join(lines)

def unit(s):
    if s.get('hardware_studio'):
        from hardware_hosting import unit as hardware_unit
        return hardware_unit(s)
    if s.get('cardboard_studio'):
        from cardboard_hosting import unit as cardboard_unit
        return cardboard_unit(s)
    base = f"/srv/webapps/{s['domain']}/current"
    return f'''[Unit]
Description=Independent FastAPI site: {s['domain']}
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
User={s['user']}
Group={s['user']}
WorkingDirectory={base}
EnvironmentFile=/etc/webapps/{s['slug']}.env
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart={base}/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port {s['port']} --workers ${{WEB_WORKERS}} --proxy-headers --forwarded-allow-ips 127.0.0.1 --timeout-keep-alive 10 --timeout-graceful-shutdown 20 --no-server-header --no-access-log
Restart=on-failure
RestartSec=3
TimeoutStopSec=30
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
CapabilityBoundingSet=
AmbientCapabilities=
UMask=0027
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''


def official_routes(s, prefix=''):
    if not s.get('codi_official'): return []
    paths=('official-head','official-history','official-directory','official-channel','official-ingest/challenge','official-ingest/use')
    lines=[]
    for name in paths:
        lines.append('\thandle '+prefix+'/'+name+' {')
        if prefix: lines.append('\t\turi strip_prefix '+prefix)
        lines.extend(['\t\treverse_proxy 127.0.0.1:8145','\t}'])
    return lines

def room_routes(s, prefix=''):
    if s.get('codi_chat_disabled'):
        return ['\t@codi_chat_paused path '+prefix+'/rooms '+prefix+'/rooms/* '+prefix+'/api/v1/room-control/*',
                '\thandle @codi_chat_paused {', '\t\trespond "Chat is temporarily unavailable while the replacement is developed" 503', '\t}']
    if not s.get('codi_rooms'): return []
    readers=[]
    if s.get('codi_readers'):
        readers=[
            '\t@codi_readers path '+prefix+'/rooms/readers/authority '+prefix+'/rooms/readers/health '+prefix+'/rooms/readers/use',
            '\thandle @codi_readers {',
            *(['\t\turi strip_prefix '+prefix] if prefix else []),
            '\t\trequest_body {', '\t\t\tmax_size 128KiB', '\t\t}',
            '\t\treverse_proxy 127.0.0.1:8143', '\t}',
        ]
    if s.get('codi_readers')=='active':
        readers += [
            '\t@codi_legacy_reader {', '\t\tpath '+prefix+'/rooms/use', '\t\theader Codi-Reader *', '\t}',
            '\thandle @codi_legacy_reader {', '\t\trespond "Reader discovery moved; reload the desktop" 410', '\t}',
        ]
    return readers+[
        '\t@codi_rooms path '+prefix+'/rooms/challenge '+prefix+'/rooms/use',
        '\thandle @codi_rooms {',
        *(['\t\turi strip_prefix '+prefix] if prefix else []),
        '\t\trequest_body {', '\t\t\tmax_size 128KiB', '\t\t}',
        '\t\treverse_proxy 127.0.0.1:8141', '\t}',
    ]


def connected_preview(s):
    # Only the validated KSU flag can activate these fixed loopback targets.
    if s.get('codi_mount','/hidden')=='':
        return connected_root(s)
    return [
        '\t@codi_preview path /hidden /hidden/*',
        '\theader @codi_preview >Cache-Control "no-store"',
        '\theader @codi_preview >Content-Security-Policy "default-src \'none\'; script-src \'self\' \'wasm-unsafe-eval\'; connect-src \'self\' wss://ksu.codes; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; worker-src \'self\' blob:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"',
        '\thandle /hidden {', '\t\tredir * /hidden/ 308', '\t}',
        '\thandle /hidden/rendezvous {', '\t\treverse_proxy 127.0.0.1:8119', '\t}',
        *official_routes(s, '/hidden'),
        *room_routes(s, '/hidden'),
        *(['\thandle /hidden/gateway/* {', '\t\turi strip_prefix /hidden', '\t\trequest_body {', '\t\t\tmax_size 12MiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8140', '\t}'] if s.get('codi_files') else []),
        '\thandle_path /hidden/* {',
        '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}',
        '\t\troute {',
        *(['\t\t\t@codi_frontend path /app.js /style.css /terminal.js /assets/terminal-initramfs.cpio.gz /desktop-apps.js /networking.js', '\t\t\thandle @codi_frontend {', '\t\t\t\troot * /srv/codi-connected/frontends/'+s['codi_frontend'], '\t\t\t\tfile_server', '\t\t\t}'] if s.get('codi_frontend') else []),
        *(['\t\t\thandle_path /assets/speech/* {','\t\t\t\troot * /srv/codi-connected/speech/'+s['codi_speech'],'\t\t\t\tfile_server','\t\t\t}'] if s.get('codi_speech') else []),
        '\t\t\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
        '\t\t\treverse_proxy @codi_identity 127.0.0.1:8118',
        '\t\t\treverse_proxy 127.0.0.1:8132', '\t\t}', '\t}',
    ]

WEBSITE_PATHS = '/blog /blog/* /posts /posts/* /static /static/* /robots.txt /healthz /test-time /test-time/* /desktop /desktop/*'
DESKTOP_CSP = "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self' wss://ksu.codes; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"

SIMPLIFIED_CSP = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self' wss://ksu.codes; font-src 'self' data:; frame-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'"

def simplified_routes(s):
    if not s.get('codi_simplified'):
        return []
    cookie = ['\t\theader Cookie *codi_simplified_preview=1*'] if s.get('codi_simplified_mode')=='preview' else []
    normal = SIMPLIFIED_CSP
    notebook = normal.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'")
    return [
        '\t@codi_simplified_normal {', *cookie, '\t\tnot path '+WEBSITE_PATHS+' /hidden /hidden/* /assets/desktop/apps/notebook/*'+(' /assets/desktop/apps/browser/*/src/engine-worker.js' if s.get('codi_browser_relay') else '')+(' / /index.html' if s.get('codi_microduck_runner') else ''), '\t}',
        '\t@codi_simplified_notebook {', *cookie, '\t\tpath /assets/desktop/apps/notebook/*', '\t}',
        *(['\t@codi_browser_worker {', '\t\tpath /assets/desktop/apps/browser/*/src/engine-worker.js', '\t}',
           '\theader @codi_browser_worker >Content-Security-Policy "'+normal.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' blob: 'wasm-unsafe-eval'")+'"',
           '\theader @codi_browser_worker >Cache-Control "no-store"',
           '\theader @codi_browser_worker >Cross-Origin-Opener-Policy "same-origin"',
           '\theader @codi_browser_worker >Cross-Origin-Embedder-Policy "require-corp"'] if s.get('codi_browser_relay') else []),
        '\theader @codi_simplified_normal >Content-Security-Policy "'+normal+'"',
        *document_lines(s,normal),
        '\theader @codi_simplified_notebook >Content-Security-Policy "'+notebook+'"',
        '\theader @codi_simplified_normal >Cache-Control "no-store"',
        '\theader @codi_simplified_notebook >Cache-Control "no-store"',
        '\theader @codi_simplified_normal >Cross-Origin-Opener-Policy "same-origin"',
        '\theader @codi_simplified_normal >Cross-Origin-Embedder-Policy "require-corp"',
        '\theader @codi_simplified_notebook >Cross-Origin-Opener-Policy "same-origin"',
        '\theader @codi_simplified_notebook >Cross-Origin-Embedder-Policy "require-corp"',
        '\t@codi_simplified_worker {', *cookie, '\t\tpath /assets/desktop/offline-worker.js', '\t}',
        '\theader @codi_simplified_worker >Service-Worker-Allowed "/"',
        '\t@codi_simplified_assets {', *cookie,
        '\t\tpath / /index.html /bootstrap.js /app.js /reference.js /desktop-apps.js /style.css /terminal.js /.build/v86/* /assets/* /network/* /storage/*',
        '\t\tnot path /assets/speech/*', '\t}',
        '\thandle @codi_simplified_assets {',
        '\t\troot * /srv/codi-connected/simplified/'+s['codi_simplified'],
        '\t\tfile_server', '\t}',
        '\thandle /codi-guest-cookie {', '\t\trewrite * /', '\t\treverse_proxy 127.0.0.1:8132', '\t}',
    ]

def connected_root(s):
    # The native backends must already be configured at the actual root mount.
    # Reserved website routes retain their existing paths, backend and policy.
    return [
        '\t@codi_root {', '\t\tnot path '+WEBSITE_PATHS+' /hidden /hidden/*', *(['\t\tnot header Cookie *codi_simplified_preview=1*'] if s.get('codi_simplified_mode')=='preview' else []), *(['\t\tnot path / /index.html /bootstrap.js /app.js /reference.js /desktop-apps.js /style.css /terminal.js /.build/v86/* /assets/* /network/* /storage/* /config.json /api/* /gateway/* /codi-guest-cookie /guest-access/* /guest-network'] if s.get('codi_simplified_mode')=='active' else []), '\t}',
        '\theader @codi_root >Cache-Control "no-store"',
        '\theader @codi_root >Content-Security-Policy "'+DESKTOP_CSP+'"',
        '\t@codi_website path '+WEBSITE_PATHS,
        '\thandle @codi_website {', '\t\treverse_proxy 127.0.0.1:'+str(s['port'])+' {',
        '\t\t\ttransport http {', '\t\t\t\tkeepalive 4s', '\t\t\t}', '\t\t}', '\t}',
        '\t@codi_old_preview path /hidden /hidden/*',
        '\thandle @codi_old_preview {', '\t\tredir * / 308', '\t}',
        *simplified_routes(s),
        *(['\t@codi_source_login path /browser-sources /browser-sources/*', '\thandle @codi_source_login {', '\t\trespond \"Sign in, open Browser, and select Licenses & source.\" 401', '\t}'] if s.get('codi_browser_sources') else []),
        *(['\thandle /browser-relay/* {', '\t\treverse_proxy unix//run/codi-browser/relay.sock {',
           '\t\t\theader_up X-Codi-Client-IP {http.request.remote.host}', '\t\t}', '\t}'] if s.get('codi_browser_relay') else []),
        '\thandle /rendezvous {', ('\t\trespond \"Chat is temporarily unavailable\" 503' if s.get('codi_chat_disabled') and not s.get('codi_p2p_steward') else '\t\treverse_proxy 127.0.0.1:8119'), '\t}',
        *official_routes(s),
        *room_routes(s),
        *(['\thandle /gateway/* {', '\t\trequest_body {', ('\t\t\tmax_size 192MiB' if s.get('codi_large_files') else '\t\t\tmax_size 12MiB'), '\t\t}', '\t\treverse_proxy 127.0.0.1:8140', '\t}'] if s.get('codi_files') else []),
        *(['\thandle_path /assets/speech/* {', '\t\troot * /srv/codi-connected/speech/'+s['codi_speech'], '\t\tfile_server', '\t}'] if s.get('codi_speech') else []),
        *(['\thandle /api/v1/auth {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}',
           '\t\treverse_proxy 127.0.0.1:8117 {', '\t\t\theader_up X-Codi-Client-IP {http.request.remote.host}', '\t\t}', '\t}'] if s.get('codi_login_filter') else []),
        '\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
        '\thandle @codi_identity {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8118', '\t}',
        '\thandle {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8132', '\t}',
    ]

def caddy(data, mode):
    validate(data)
    if mode not in ['prepare','production']:
        raise ValueError('Invalid mode')
    lines = [f'# webhost-sites mode: {mode}', '{', '\tadmin unix//run/caddy/admin.sock', *(['\thttp_port 8080', '\thttps_port 8443', '\tdefault_bind 127.0.0.1'] if data.get('codi_shared_ingress') and mode=='production' else []), '\tservers {', '\t\tprotocols h1 h2', *(['\t\tlistener_wrappers {', '\t\t\tproxy_protocol {', '\t\t\t\ttimeout 1s', '\t\t\t\tallow 127.0.0.1/32', '\t\t\t\tfallback_policy reject', '\t\t\t}', '\t\t\ttls', '\t\t}'] if data.get('codi_shared_ingress') and mode=='production' else []), '\t}', '}', '', '(site_defaults) {', '\tencode zstd gzip', '\theader ?Cache-Control "no-cache, max-age=0, must-revalidate"', '\theader {', '\t\tX-Content-Type-Options nosniff', '\t\tReferrer-Policy no-referrer', '\t\tContent-Security-Policy "default-src \'none\'; style-src \'self\'; img-src \'self\'; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"', '\t}', '}', '']
    for s in data['sites']:
        if not s['enabled']:
            continue
        address = 'http://'+s['domain'] if mode=='prepare' else s['domain']
        lines += [address+' {']
        if mode=='prepare': lines += ['\tbind 127.0.0.1']
        if s['domain'] == 'ksu.codes':
            lines += ['\t@test_time path /test-time/*', '\theader @test_time >Content-Security-Policy "default-src \'none\'; script-src \'self\'; connect-src \'self\'; style-src \'self\'; img-src \'self\' data:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"']
        if s['domain'] == 'ksu.codes':
            lines += ['\t@desktop path /desktop/*', '\theader @desktop >Content-Security-Policy "default-src \'none\'; script-src \'self\' \'wasm-unsafe-eval\'; connect-src \'self\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; worker-src \'self\' blob:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"']
        lines += ['\timport site_defaults', '\tlog {', f"\t\toutput file /var/log/caddy/{s['slug']}.json {{", '\t\t\troll_size 10MiB', '\t\t\troll_keep 3', '\t\t\troll_keep_for 168h', '\t\t}', '\t\tformat json', '\t}']
        if s.get('hardware_studio'):
            # Never retain the server-issued workspace token in access logs.
            lines[-2:-1] = ['\t\tformat filter {', '\t\t\twrap json', '\t\t\tfields {', '\t\t\t\trequest>headers>X-Workspace-Token delete', '\t\t\t}', '\t\t}']
            from hardware_hosting import caddy_lines
            lines += caddy_lines(s)
        if s.get('cardboard_studio'):
            from cardboard_hosting import caddy_lines
            lines += caddy_lines(s)
        upstream = [f"\treverse_proxy 127.0.0.1:{s['port']} {{", '\t\ttransport http {', '\t\t\tkeepalive 4s', '\t\t}', '\t}']
        if s.get('codi_preview',False):
            lines += connected_preview(s)
            upstream = [] if s.get('codi_mount','/hidden')=='' else ['\thandle {']+['\t'+line for line in upstream]+['\t}']
        lines += upstream+['}', '']
    for s in data['sites']:
        lines += site_lines(s,mode)
    if data.get('codi_beta_simplified'):
        address=('http://' if mode=='prepare' else '')+'beta.ksu.codes'
        lines += [address+' {']
        if mode=='prepare':lines += ['\tbind 127.0.0.1']
        if data.get('codi_beta_maintenance'):
            # A 200 maintenance document avoids the old service worker's
            # offline fallback to the cached unguarded desktop on 5xx.
            lines += ['\timport site_defaults','\theader >Cache-Control "no-store"','\t@beta_gate_entry path / /index.html','\thandle @beta_gate_entry {','\t\theader Content-Type "text/html; charset=utf-8"','\t\trespond "<!doctype html><title>Beta maintenance</title><p>Beta is temporarily unavailable while storage is updated.</p>" 200','\t}','\thandle {','\t\trespond "Beta maintenance" 503','\t}','}', '']
        else:
            beta_csp=SIMPLIFIED_CSP.replace('wss://ksu.codes','wss://beta.ksu.codes')
            beta_notebook=beta_csp.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'")
            lines += ['\timport site_defaults',
                      '\t@beta_normal not path /assets/desktop/apps/notebook/*',
                      '\t@beta_notebook path /assets/desktop/apps/notebook/*',
                      '\theader @beta_normal >Content-Security-Policy "'+beta_csp+'"',
                      '\theader @beta_notebook >Content-Security-Policy "'+beta_notebook+'"',
                      '\theader >Cache-Control "no-store"',
                      '\theader >Cross-Origin-Opener-Policy "same-origin"',
                      '\theader >Cross-Origin-Embedder-Policy "require-corp"',
                      '\t@beta_worker path /assets/desktop/offline-worker.js',
                      '\theader @beta_worker >Service-Worker-Allowed "/"',
                      *beta_overlay_routes(data),
                      '\t@beta_static path / /index.html /bootstrap.js /app.js /reference.js /desktop-apps.js /style.css /terminal.js /.build/v86/* /assets/* /network/* /storage/*',
                      '\thandle @beta_static {', '\t\troot * /srv/codi-connected/simplified/'+data['codi_beta_simplified'], '\t\tfile_server', '\t}',
                      '\thandle /gateway/* {', '\t\trequest_body {', '\t\t\tmax_size 192MiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:28140', '\t}',
                      '\t@beta_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
                      '\thandle @beta_identity {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:28118', '\t}',
                      '\thandle /codi-guest-cookie {', '\t\trewrite * /', '\t\treverse_proxy 127.0.0.1:28132', '\t}',
                      '\thandle /guest-network {', '\t\trespond "Beta guest networking is unavailable" 503', '\t}',
                      '\t@beta_guest path /config.json /guest-access/*',
                      '\thandle @beta_guest {', '\t\treverse_proxy 127.0.0.1:28132', '\t}',
                      '\thandle {', '\t\trespond "Not found" 404', '\t}', '}', '']
    if any(s.get('codi_turn_certificate',False) for s in data['sites']):
        lines += [('http://' if mode=='prepare' else '')+'turn.ksu.codes {']
        if mode=='prepare': lines += ['\tbind 127.0.0.1']
        lines += ['\timport site_defaults', '\trespond \"Not found\" 404', '}', '']
    lines += [':8080 {' if data.get('codi_shared_ingress') and mode=='production' else ':80 {']
    if mode=='prepare': lines += ['\tbind 127.0.0.1']
    lines += ['\trespond "Not found" 404', '}', '']
    return '\n'.join(lines)
