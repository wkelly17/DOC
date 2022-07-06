<script lang="ts">
  import { onMount } from 'svelte'
  import type { AssemblyStrategy } from './types'
  import LoadingIndicator from './components/LoadingIndicator.svelte'
  import AssemblyStrategyComponent from './components/AssemblyStrategy.svelte'
  import Button, { Label } from '@smui/button'
  import Autocomplete from '@smui-extra/autocomplete'
  // import { Text } from '@smui/list'
  // import CircularProgress from '@smui/circular-progress'
  import Checkbox from '@smui/checkbox'
  import FormField from '@smui/form-field'
  import Switch from '@smui/switch'
  import LayoutGrid, { Cell } from '@smui/layout-grid'

  import otBooks from './data/ot_books'

  // Wizard components
  // https://github.com/MirrorBytes/MultiStep/tree/main/step-4/src/components
  // FIXME If I use other form elements than select and input then I
  // will need to add such a component import here (and create it).
  // import Form from './components/Form.svelte'
  // import Step from './components/Step.svelte'
  // import Input from './components/Input.svelte'
  // import Select from './components/Select.svelte'

  let API_ROOT_URL: string = <string>import.meta.env.VITE_BACKEND_API_URL
  console.log('API_ROOT_URL: ', API_ROOT_URL)

  function isEmpty(value: string | null | undefined): boolean {
    return value === undefined || value === null || value.trim()?.length === 0
  }

  const LANGUAGE_BOOK_ORDER: string = 'lbo'

  let email: string | null = null
  let assemblyStrategy: AssemblyStrategy | null
  let assemblyStrategyKind: string = LANGUAGE_BOOK_ORDER // Default to language book order since the UI is defaulted to print
  let layoutForPrint: boolean = true
  let generatePdf: boolean = false
  let generateEpub: boolean = false
  let generateDocx: boolean = false
  let lang0NameAndCode: string = ''
  let lang0ResourceTypes: string[] = []
  let lang0ResourceCodes: string[] = []
  let lang1NameAndCode: string = ''
  let lang1ResourceTypes: string[] = []
  let lang1ResourceCodes: string[] = []

  // Button will toggle this value
  let showAnotherLang: boolean = false
  function handleAddLang() {
    showAnotherLang = true
  }

  onMount(() => {
    reset()
  })

  const LANGUAGE_CODES_AND_NAMES: string = '/language_codes_and_names'
  const RESOURCE_TYPES_AND_NAMES_FOR_LANG: string = '/resource_types_and_names_for_lang/'
  const RESOURCE_CODES_FOR_LANG: string = '/resource_codes_for_lang/'

  // Language 0

  async function getLang0CodesAndNames(): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang0ResourceTypesAndNames(langCode: string): Promise<string[]> {
    const response = await fetch(
      API_ROOT_URL + RESOURCE_TYPES_AND_NAMES_FOR_LANG + langCode
    )
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang0ResourceCodes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_CODES_FOR_LANG + langCode)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  // Language 1

  async function getLang1CodesAndNames(): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang1ResourceTypesAndNames(langCode: string): Promise<string[]> {
    const response = await fetch(
      API_ROOT_URL + RESOURCE_TYPES_AND_NAMES_FOR_LANG + langCode
    )
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang1ResourceCodes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_CODES_FOR_LANG + langCode)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  let document_request_key: string = ''

  function reset() {
    assemblyStrategyKind = LANGUAGE_BOOK_ORDER
    // Be careful to set email to null as API expects a null rather
    // than empty string if email is not provided by user.
    email = null
    layoutForPrint = true
    generatePdf = false
    generateEpub = false
    generateDocx = false
    lang0NameAndCode = ''
    lang0ResourceTypes = []
    lang0ResourceCodes = []
    lang1NameAndCode = ''
    lang1ResourceTypes = []
    lang1ResourceCodes = []
    hideWaitMessage()
    hideErrorMessage()
    hideLinksMessage()
    document_request_key = ''
    showAnotherLang = false
    document.getElementById('lang')?.focus()
  }

  // Submit button will toggle this value
  let waitMessage: boolean
  $: waitMessage = false
  function hideWaitMessage() {
    waitMessage = false
  }
  function showWaitMessage() {
    waitMessage = true
  }
  // Error will toggle this value
  let errorMessage: boolean
  $: errorMessage = false
  // let errorMessageDetails: string | null
  // $: errorMessageDetails = null
  function hideErrorMessage() {
    errorMessage = false
  }
  function showErrorMessage() {
    errorMessage = true
  }
  let linksMessage: boolean
  $: linksMessage = false
  function showLinksMessage() {
    linksMessage = true
  }
  function hideLinksMessage() {
    linksMessage = false
  }

  const langCodeRegex = /.*\(language code: (.*?)\)/

  /**
   * Extract the language code from the menu option selected.
   * Presupposes that menu options are in the following format:
   * 'English (language code: en)'
   **/
  function extractLanguageCode(languageString: string): string {
    let matchStrings = languageString.match(langCodeRegex)
    if (matchStrings) {
      return matchStrings[1]
    } else {
      throw new Error('Invalid menu selection chosen') // This won't happen, but make tsc happy
    }
  }

  function submit() {
    let rr = []
    // Create resource_requests for lang0
    for (let resourceCode of lang0ResourceCodes) {
      for (let resourceType of lang0ResourceTypes) {
        rr.push({
          lang_code: extractLanguageCode(lang0NameAndCode),
          resource_type: resourceType,
          resource_code: resourceCode
        })
      }
    }
    // Create resource_requests for lang1
    for (let resourceCode of lang1ResourceCodes) {
      for (let resourceType of lang1ResourceTypes) {
        rr.push({
          lang_code: extractLanguageCode(lang1NameAndCode),
          resource_type: resourceType,
          resource_code: resourceCode
        })
      }
    }

    console.log('email: ', email)
    if (layoutForPrint) {
      layoutForPrint = true
    } else {
      layoutForPrint = false
    }
    if (generatePdf) {
      generatePdf = true
    } else {
      generatePdf = false
    }
    if (generateEpub) {
      generateEpub = true
    } else {
      generateEpub = false
    }
    if (generateDocx) {
      generateDocx = true
    } else {
      generateDocx = false
    }

    // Create the JSON structure to POST.
    // let documentRequest: DocumentRequest = {
    let documentRequest = {
      // FIXME Test that email_address is handled correctly with respect to null
      email_address: email?.trim(), // !isEmpty(email) ? email.trim() : null,
      // email_address: !isEmpty(email) ? email.trim() : null,
      assembly_strategy_kind: assemblyStrategyKind,
      // assembly_layout_kind: undefined,
      layout_for_print: layoutForPrint,
      generate_pdf: generatePdf,
      generate_epub: generateEpub,
      generate_docx: generateDocx,
      resource_requests: rr
    }
    console.log('document request: ', JSON.stringify(documentRequest, null, 2))
    if (errorMessage) {
      hideErrorMessage()
    }
    showWaitMessage()
    hideLinksMessage()
    // POST the formValues to the API
    fetch(API_ROOT_URL + '/documents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(documentRequest)
    })
      .then(response => {
        console.log('response.ok: ', response.ok)
        if (response.ok) {
          return response.json()
        } else {
          return Promise.reject('Request failed error')
        }
      })
      .then(data => {
        console.log('data: ', data)
        document_request_key = data['finished_document_request_key']
        hideErrorMessage()
        hideWaitMessage()
        showLinksMessage()
      })
      .catch(err => {
        console.error('error: ', err)
        hideWaitMessage()
        // Currently we don't display this error to the user, but we could
        // display it alongside the canned generic error message.
        // errorMessageDetails = JSON.stringify(err)
        showErrorMessage()
        hideLinksMessage()
      })
  }
</script>

<main>
  <div class="forms">
    <div>
      <h2>{import.meta.env.VITE_TOP_H2_HEADER}</h2>

      <form on:submit|preventDefault={submit}>
        <div>
          {#await getLang0CodesAndNames()}
            <LoadingIndicator />
          {:then data}
            <Autocomplete
              options={data.map(function (element) {
                return element[1]
              })}
              bind:value={lang0NameAndCode}
              showMenuWithNoInput={false}
              label={import.meta.env.VITE_LANG_0_HEADER}
            />
          {:catch error}
            <p class="error">{error.message}</p>
          {/await}
        </div>
        {#if !isEmpty(lang0NameAndCode)}
          {@const lang0Code = extractLanguageCode(lang0NameAndCode)}
          <div>
            {#await getLang0ResourceTypesAndNames(lang0Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_0_RESOURCE_TYPES_HEADER}</h3>
              {#each data as resourceType}
                <FormField align="end">
                  <Checkbox
                    bind:group={lang0ResourceTypes}
                    bind:value={resourceType[0]}
                  />
                  <span slot="label">{resourceType[1]}</span>
                </FormField>
                <br />
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}

        {#if !isEmpty(lang0NameAndCode) && lang0ResourceTypes?.length > 0}
          {@const lang0Code = extractLanguageCode(lang0NameAndCode)}
          <div>
            {#await getLang0ResourceCodes(lang0Code)}
              <LoadingIndicator />
            {:then data}
              {@const otBooksInLang0 = data.filter(function (element) {
                return otBooks.includes(element[0])
              })}
              {@const ntBooksInLang0 = data.filter(function (element) {
                return !otBooks.includes(element[0])
              })}
              <h3>{import.meta.env.VITE_LANG_0_RESOURCE_CODES_HEADER}</h3>
              <LayoutGrid>
                <Cell>
                  <h3>Old Testament</h3>
                  {#each otBooksInLang0 as resourceCodeAndName}
                    <div class="book-cell">
                      <FormField align="end">
                        <Checkbox
                          bind:group={lang0ResourceCodes}
                          bind:value={resourceCodeAndName[0]}
                        />
                        <span slot="label">{resourceCodeAndName[1]}</span>
                      </FormField>
                    </div>
                  {/each}
                </Cell>
                <Cell>
                  <h3>New Testament</h3>
                  {#each ntBooksInLang0 as resourceCodeAndName}
                    <div class="book-cell">
                      <FormField align="end">
                        <Checkbox
                          bind:group={lang0ResourceCodes}
                          bind:value={resourceCodeAndName[0]}
                        />
                        <span slot="label">{resourceCodeAndName[1]}</span>
                      </FormField>
                    </div>
                  {/each}
                </Cell>
              </LayoutGrid>
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}

        {#if !isEmpty(lang0NameAndCode) && lang0ResourceTypes?.length > 0 && lang0ResourceCodes?.length > 0}
          <button disabled={showAnotherLang} on:click|preventDefault={handleAddLang}
            >{import.meta.env.VITE_ADD_ANOTHER_LANGUAGE_BUTTON_TXT}</button
          >
        {/if}
        {#if showAnotherLang}
          <div>
            <h3>{import.meta.env.VITE_LANG_1_HEADER}</h3>
            {#await getLang1CodesAndNames()}
              <LoadingIndicator />
            {:then data}
              <Autocomplete
                options={data.map(function (element) {
                  return element[1]
                })}
                bind:value={lang1NameAndCode}
                showMenuWithNoInput={false}
                label={import.meta.env.VITE_LANG_1_HEADER}
              />
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang1NameAndCode)}
          {@const lang1Code = extractLanguageCode(lang1NameAndCode)}
          <div>
            {#await getLang1ResourceTypesAndNames(lang1Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_1_RESOURCE_TYPES_HEADER}</h3>
              {#each data as resourceType}
                <div>
                  <FormField align="end">
                    <Checkbox
                      bind:group={lang1ResourceTypes}
                      bind:value={resourceType[0]}
                    />
                    <span slot="label">{resourceType[1]}</span>
                  </FormField>
                </div>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang1NameAndCode) && lang1ResourceTypes?.length > 0}
          {@const lang1Code = extractLanguageCode(lang1NameAndCode)}
          <div>
            {#await getLang1ResourceCodes(lang1Code)}
              <LoadingIndicator />
            {:then data}
              {@const otBooksInLang1 = data.filter(function (element) {
                return otBooks.includes(element[0])
              })}
              {@const ntBooksInLang1 = data.filter(function (element) {
                return !otBooks.includes(element[0])
              })}
              <h3>{import.meta.env.VITE_LANG_1_RESOURCE_CODES_HEADER}</h3>
              <LayoutGrid>
                <Cell>
                  <h3>Old Testament</h3>
                  {#each otBooksInLang1 as resourceCodeAndName}
                    <div class="book-cell">
                      <FormField align="end">
                        <Checkbox
                          bind:group={lang1ResourceCodes}
                          bind:value={resourceCodeAndName[0]}
                        />
                        <span slot="label">{resourceCodeAndName[1]}</span>
                      </FormField>
                    </div>
                  {/each}
                </Cell>
                <Cell>
                  <h3>New Testament</h3>
                  {#each ntBooksInLang1 as resourceCodeAndName}
                    <div class="book-cell">
                      <FormField align="end">
                        <Checkbox
                          bind:group={lang1ResourceCodes}
                          bind:value={resourceCodeAndName[0]}
                        />
                        <span slot="label">{resourceCodeAndName[1]}</span>
                      </FormField>
                    </div>
                  {/each}
                </Cell>
              </LayoutGrid>
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        <div>
          <FormField align="end">
            <Switch bind:checked={layoutForPrint} />
            <span slot="label">{import.meta.env.VITE_LAYOUT_FOR_PRINT_LABEL}</span>
          </FormField>
        </div>
        <div
          class:assembly-strategy-invisible={lang1ResourceCodes === undefined ||
            lang1ResourceCodes.length == 0 ||
            layoutForPrint}
        >
          <AssemblyStrategyComponent bind:assemblyStrategy />
        </div>
        <div>
          <FormField align="end">
            <Switch bind:checked={generatePdf} />
            <span slot="label">{import.meta.env.VITE_PDF_LABEL}</span>
          </FormField>
        </div>
        <div>
          <FormField align="end">
            <Switch bind:checked={generateEpub} />
            <span slot="label">{import.meta.env.VITE_EPUB_LABEL}</span>
          </FormField>
        </div>
        <div>
          <FormField align="end">
            <Switch bind:checked={generateDocx} />
            <span slot="label">{import.meta.env.VITE_DOCX_LABEL}</span>
          </FormField>
        </div>

        <div class="fields">
          <label for="email">{import.meta.env.VITE_EMAIL_LABEL}</label>
          <input type="text" name="email" id="email" bind:value={email} />
        </div>
        <div style="margin-top:3em">
          <Button
            color="secondary"
            on:click={submit}
            variant="unelevated"
            class="submit-button"
          >
            <Label>Generate document</Label>
          </Button>
          <Button
            color="secondary"
            on:click={reset}
            variant="unelevated"
            class="reset-button"
          >
            <Label>Reset</Label>
          </Button>
        </div>
      </form>

      {#if waitMessage}
        <div class="wait-message">
          <p>{import.meta.env.VITE_WAIT_MSG}</p>
        </div>
      {/if}
      {#if errorMessage}
        <div class="error-message">
          <p>{import.meta.env.VITE_ERROR_MSG}</p>
        </div>
      {/if}
      {#if document_request_key.length > 0 && linksMessage}
        <div class="finished-document-url">
          <p>
            {import.meta.env.VITE_HTML_DOCUMENT_READY_MSG_PART1}
            <a href="{API_ROOT_URL}/html/{document_request_key}" target="_blank"
              >{import.meta.env.VITE_HTML_DOCUMENT_READY_LINK_TXT}</a
            >
            {import.meta.env.VITE_HTML_DOCUMENT_READY_MSG_PART2}
          </p>
          {#if generateEpub}
            <p>
              {import.meta.env.VITE_EPUB_DOCUMENT_READY_MSG_PART1}
              <a href="{API_ROOT_URL}/epub/{document_request_key}"
                >{import.meta.env.VITE_EPUB_DOCUMENT_READY_LINK_TXT}</a
              >
              {import.meta.env.VITE_EPUB_DOCUMENT_READY_MSG_PART2}
            </p>
          {/if}
          {#if generatePdf}
            <p>
              {import.meta.env.VITE_PDF_DOCUMENT_READY_MSG_PART1}
              <a href="{API_ROOT_URL}/pdf/{document_request_key}"
                >{import.meta.env.VITE_PDF_DOCUMENT_READY_LINK_TXT}</a
              >
              {import.meta.env.VITE_PDF_DOCUMENT_READY_MSG_PART2}
            </p>
          {/if}
          {#if generateDocx}
            <p>
              {import.meta.env.VITE_DOCX_DOCUMENT_READY_MSG_PART1}
              <a href="{API_ROOT_URL}/docx/{document_request_key}"
                >{import.meta.env.VITE_DOCX_DOCUMENT_READY_LINK_TXT}</a
              >
              {import.meta.env.VITE_DOCX_DOCUMENT_READY_MSG_PART2}
            </p>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</main>

<style>
  :global(body) {
    font-family: Arial, Helvetica, sans-serif;
    /* background-color: #f3f3f3; */
  }
  :global(*, *:before, *:after) {
    box-sizing: border-box;
  }
  :global(input[type='text'], input[type='select'], input[type='password'], input[type='number'], select) {
    padding: 5px;
    min-width: 30em;
  }
  .fields {
    margin: 2em 0;
  }
  .fields label {
    display: block;
    margin-top: 1em;
  }
  .forms {
    margin: 2em 5em 2em 10em;
  }
  main {
    display: flex;
  }
  .error {
    color: red;
  }
  * :global(.submit-button) {
    background-color: green;
    border: none;
    color: white;
    padding: 15px 30px;
    text-decoration: none;
    margin: 4px 2px;
    cursor: pointer;
  }
  * :global(.reset-button) {
    background-color: red;
    border: none;
    color: white;
    padding: 15px 30px;
    text-decoration: none;
    margin: 4px 2px;
    cursor: pointer;
  }
  * :global(.lang0-codes-text-input) {
    display: flex;
    width: 100%;
    justify-content: center;
    align-items: center;
  }
  * :global(.circular-progress) {
    height: 24px;
    width: 24px;
  }
  .assembly-strategy-invisible {
    display: none;
  }
  .book-cell {
    display: flex;
    justify-content: left;
    align-items: center;
  }
</style>
