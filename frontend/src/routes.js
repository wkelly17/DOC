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

  '*': ViewNotFound
}
