import Books from './components/Books.svelte'
import ResourceTypes from './components/ResourceTypes.svelte'
import Languages from './components/Languages.svelte'
import Home from './components/Home.svelte'
import About from './components/About.svelte'
import Settings from './components/Settings.svelte'
import Result from './components/Result.svelte'
import ViewNotFound from './components/ViewNotFound.svelte'

// v1 release Components
import Home_v1 from './components/v1_release/Home_v1.svelte'
import Languages_v1 from './components/v1_release/Languages_v1.svelte'
import Books_v1 from './components/v1_release/Books_v1.svelte'
import Result_v1 from './components/v1_release/Result_v1.svelte'
import About_v1 from './components/v1_release/About_v1.svelte'

export default {
  '/': Home,
  '/languages': Languages,
  '/books': Books,
  '/resource_types': ResourceTypes,
  '/settings': Settings,
  '/result': Result,
  '/about': About,

  // v1 release routes
  '/v1/': Home_v1,
  '/v1/languages': Languages_v1,
  '/v1/books': Books_v1,
  '/v1/result': Result_v1,
  '/v1/about': About_v1,

  '*': ViewNotFound
}
