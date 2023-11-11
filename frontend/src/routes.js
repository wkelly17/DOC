import Home from './components/Home.svelte'
import Languages from './components/Languages.svelte'
import Books from './components/Books.svelte'
import ResourceTypes from './components/ResourceTypes.svelte'
import Settings from './components/Settings.svelte'
import ViewNotFound from './components/ViewNotFound.svelte'

export default {
  '/': Home,
  '/languages': Languages,
  '/books': Books,
  '/resource_types': ResourceTypes,
  '/settings': Settings,
  '*': ViewNotFound
}
