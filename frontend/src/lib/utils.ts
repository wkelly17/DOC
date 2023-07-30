import {
  glLangCodeAndNamesStore,
  nonGlLangCodeAndNamesStore,
  lang0NameAndCodeStore,
  lang1NameAndCodeStore,
  lang0CodeStore,
  lang1CodeStore,
  lang0NameStore,
  lang1NameStore,
  langCountStore
} from '../stores/LanguagesStore'
import { otBookStore, ntBookStore, bookCountStore } from '../stores/BooksStore'
import {
  lang0ResourceTypesStore,
  lang1ResourceTypesStore,
  resourceTypesCountStore,
  twResourceRequestedStore
} from '../stores/ResourceTypesStore'
import {
  documentReadyStore,
  errorStore,
  resetValuesStore
} from '../stores/NotificationStore'
import {
  layoutForPrintStore,
  assemblyStrategyKindStore,
  generatePdfStore,
  generateEpubStore,
  generateDocxStore,
  emailStore,
  documentRequestKeyStore
} from '../stores/SettingsStore'

const languageBookOrder: string = <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER

type StoreGroup = 'languages' | 'books' | 'resource_types' | 'settings' | 'notifications'

export function resetStores(storeGroup: StoreGroup) {
  if (storeGroup === 'languages') {
    glLangCodeAndNamesStore.set([])
    nonGlLangCodeAndNamesStore.set([])
    lang0NameAndCodeStore.set('')
    lang1NameAndCodeStore.set('')
    lang0CodeStore.set('')
    lang1CodeStore.set('')
    lang0NameStore.set('')
    lang1NameStore.set('')
    langCountStore.set(0)
  }

  if (storeGroup === 'books') {
    otBookStore.set([])
    ntBookStore.set([])
    bookCountStore.set(0)
  }

  if (storeGroup === 'resource_types') {
    lang0ResourceTypesStore.set([])
    lang1ResourceTypesStore.set([])
    resourceTypesCountStore.set(0)
  }

  if (storeGroup === 'settings') {
    layoutForPrintStore.set(false)
    assemblyStrategyKindStore.set(languageBookOrder)
    generatePdfStore.set(true)
    generateEpubStore.set(false)
    generateDocxStore.set(false)
    // emailStore.set(null)
    documentRequestKeyStore.set('')
    twResourceRequestedStore.set(false)
  }

  if (storeGroup === 'notifications') {
    documentReadyStore.set(false)
    errorStore.set(null)
  }
}

export function getApiRootUrl(): string {
  if (<boolean>import.meta.env.PROD) {
    // @ts-ignore
    console.log(`BACKEND_API_URL: ${window.env.BACKEND_API_URL}`)
    // @ts-ignore
    return <string>window.env.BACKEND_API_URL
  } else {
    // If we are running the frontend with 'npm run dev' then this
    // else will be used
    console.log(`BACKEND_API_URL: ${<string>import.meta.env.VITE_DEV_BACKEND_API_URL}`)
    return <string>import.meta.env.VITE_DEV_BACKEND_API_URL
  }
}

export function getFileServerUrl(): string {
  if (<boolean>import.meta.env.PROD) {
    // @ts-ignore
    console.log(`FILE_SERVER_URL: ${window.env.FILE_SERVER_URL}`)
    // @ts-ignore
    return <string>window.env.FILE_SERVER_URL
  } else {
    // If we are running the frontend with 'npm run dev' then this
    // else will be used
    console.log(`FILE_SERVER_URL: ${<string>import.meta.env.VITE_DEV_FILE_SERVER_URL}`)
    return <string>import.meta.env.VITE_DEV_FILE_SERVER_URL
  }
}

/**
 * Indicate whether to show Mast, Tabs, and Sidebar
 **/
export function setShowTopMatter(): boolean {
  let showTopMatter = false
  // .env vars come over as strings always by default (PROD .env var
  //  above is an exception because Vite handles setting it.
  if (<string>import.meta.env.VITE_SHOW_TOP_MATTER === 'true') {
    showTopMatter = true
  }
  return showTopMatter
}
