import {
  langCodeAndNamesStore,
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
  resourceTypesCountStore
} from '../stores/ResourceTypesStore'
import { documentReadyStore, errorStore } from '../stores/NotificationStore'
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
