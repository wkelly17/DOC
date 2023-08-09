// The dumbed-down version and the full version of the app each
// maintain their own stores since they are stateful and you
// don't want a user navigating from the dumbed-down version
// of the app to the full version to share state between them.
import {
  langCodeAndNamesStore,
  lang0NameAndCodeStore,
  lang1NameAndCodeStore,
  lang0CodeStore,
  lang1CodeStore,
  lang0NameStore,
  lang1NameStore,
  langCountStore
} from '../../stores/v1_release/LanguagesStore'
import {
  otBookStore,
  ntBookStore,
  bookCountStore
} from '../../stores/v1_release/BooksStore'
import {
  lang0ResourceTypesStore,
  lang1ResourceTypesStore,
  resourceTypesCountStore
} from '../../stores/v1_release/ResourceTypesStore'
import {
  documentReadyStore,
  errorStore,
  resetValuesStore
} from '../../stores/v1_release/NotificationStore'
import {
  layoutForPrintStore,
  assemblyStrategyKindStore,
  generatePdfStore,
  generateEpubStore,
  generateDocxStore,
  emailStore,
  documentRequestKeyStore
} from '../../stores/v1_release/SettingsStore'

const languageBookOrder: string = <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER

type StoreGroup = 'languages' | 'books' | 'resource_types' | 'settings' | 'notifications'

export function resetStores(storeGroup: StoreGroup) {
  if (storeGroup === 'languages') {
    langCodeAndNamesStore.set([])
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
    layoutForPrintStore.set(true)
    assemblyStrategyKindStore.set(languageBookOrder)
    generatePdfStore.set(false)
    generateEpubStore.set(false)
    generateDocxStore.set(false)
    emailStore.set(null)
    documentRequestKeyStore.set('')
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
  if (<string>import.meta.env.VITE_SHOW_TOP_MATTER_IN_V1 === 'true') {
    showTopMatter = true
  }
  return showTopMatter
}

export function printToConsole(s: string) {
  if (<string>import.meta.env.VITE_PRINT_TO_CONSOLE === 'true') {
    console.log(s)
  }
}

/**
 * Indicate whether to show resource types on the Home/Content page
 **/
export function setShowResourceTypes(): boolean {
  let showResourceTypes = false
  // .env vars come over as strings always by default (PROD .env var
  //  above is an exception because Vite handles setting it.
  if (<string>import.meta.env.VITE_SHOW_RESOURCE_TYPES_V1 === 'true') {
    showResourceTypes = true
  }
  return showResourceTypes
}
