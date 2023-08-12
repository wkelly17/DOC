import Books from './components/Books.svelte'
import ResourceTypes from './components/ResourceTypes.svelte'
import Languages from './components/Languages.svelte'
import Home from './components/Home.svelte'
import About from './components/About.svelte'
import Settings from './components/Settings.svelte'
import Result from './components/Result.svelte'
import ViewNotFound from './components/ViewNotFound.svelte'

// v1 release Components
import Home_v1 from './components/v1_release/Home.svelte'
import Languages_v1 from './components/v1_release/Languages.svelte'
import Books_v1 from './components/v1_release/Books.svelte'
import Result_v1 from './components/v1_release/Result.svelte'
import About_v1 from './components/v1_release/About.svelte'

// v2 release components

import Books_v2 from './components/v2_release/Books.svelte'
import ResourceTypes_v2 from './components/v2_release/ResourceTypes.svelte'
import Languages_v2 from './components/v2_release/Languages.svelte'
import Home_v2 from './components/v2_release/Home.svelte'
import About_v2 from './components/v2_release/About.svelte'
import Settings_v2 from './components/v2_release/Settings.svelte'
import Result_v2 from './components/v2_release/Result.svelte'
import ViewNotFound_v2 from './components/v2_release/ViewNotFound.svelte'

export default {
  // v1 release routes
  '/': Home_v1,
  '/languages': Languages_v1,
  '/books': Books_v1,
  '/result': Result_v1,
  '/about': About_v1,

  // experimenta/full release routes
  '/experimental/': Home,
  '/experimental/languages': Languages,
  '/experimental/books': Books,
  '/experimental/resource_types': ResourceTypes,
  '/experimental/settings': Settings,
  '/experimental/result': Result,
  '/experimental/about': About,

  // full release new ui routes
  '/v2/': Home_v2,
  '/v2/languages': Languages_v2,
  '/v2/books': Books_v2,
  '/v2/resource_types': ResourceTypes_v2,
  '/v2/settings': Settings_v2,
  '/v2/result': Result_v2,
  '/v2/about': About_v2,

  '*': ViewNotFound
}
