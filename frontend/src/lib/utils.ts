import {
  gatewayCodeAndNamesStore,
  heartCodeAndNamesStore,
  lang0NameAndCodeStore,
  lang1NameAndCodeStore,
  langCodesStore,
  langNamesStore,
  langCountStore
} from '../stores/LanguagesStore'
import { otBookStore, ntBookStore, bookCountStore } from '../stores/BooksStore'
import {
  // TODO should we include resourceTypesStore and reset it also?
  lang0ResourceTypesStore,
  lang1ResourceTypesStore,
  resourceTypesCountStore,
  twResourceRequestedStore
} from '../stores/ResourceTypesStore'
import { documentReadyStore, errorStore } from '../stores/NotificationStore'
import {
  layoutForPrintStore,
  assemblyStrategyKindStore,
  generatePdfStore,
  generateEpubStore,
  generateDocxStore,
  documentRequestKeyStore
} from '../stores/SettingsStore'

const languageBookOrder: string = <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER

type StoreGroup = 'languages' | 'books' | 'resource_types' | 'settings' | 'notifications'

export let langRegExp = new RegExp('.*languages.*')
export let bookRegExp = new RegExp('.*books.*')
export let resourceTypeRegExp = new RegExp('.*resource_types.*')
export let settingsRegExp = new RegExp('.*settings.*')

export function resetStores(storeGroup: StoreGroup) {
  if (storeGroup === 'languages') {
    gatewayCodeAndNamesStore.set([])
    heartCodeAndNamesStore.set([])
    lang0NameAndCodeStore.set('')
    lang1NameAndCodeStore.set('')
    langCodesStore.set([])
    langNamesStore.set([])
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

export function getLogRocketId(): string {
  // @ts-ignore
  console.log(`LOGROCKET_ID: ${window.env.LOGROCKET_ID}`)
  // @ts-ignore
  return <string>window.env.LOGROCKET_ID
}

/**
 * Indicate whether to show Mast, Tabs, and Sidebar
 **/

export function getName(codeAndName: string): string {
  return codeAndName?.split(/, (.*)/s)[1]
}
export function getCode(codeAndName: string): string {
  return codeAndName?.split(/, (.*)/s)[0]
}

export function getResourceTypeName(codeAndName: string): string {
  return codeAndName?.split(', ')[2]
}
export function getResourceTypeCode(codeAndName: string): string {
  return codeAndName?.split(', ')[1]
}
export function getResourceTypeLangCode(codeAndName: string): string {
  return codeAndName?.split(', ')[0]
}
