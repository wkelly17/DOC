import Books from './components/Books.svelte'
import ResourceTypes from './components/ResourceTypes.svelte'
import Languages from './components/Languages.svelte'
import Home from './components/Home.svelte'
import About from './components/About.svelte'
import Settings from './components/Settings.svelte'
import ViewNotFound from './components/ViewNotFound.svelte'
export default {
  '/': Home,
  '/languages': Languages,
  '/books': Books,
  '/resource_types': ResourceTypes,
  '/settings': Settings,
  '/about': About,
  // '/object/:objectId': ViewObject,
  '*': ViewNotFound
}
