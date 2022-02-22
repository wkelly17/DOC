<script lang="ts">
  import { onMount } from 'svelte'
  import type { AssemblyStrategy } from './lib/types'
  import LoadingIndicator from './lib/LoadingIndicator.svelte'
  import AssemblyStrategyComponent from './lib/AssemblyStrategy.svelte'

  let API_ROOT_URL: string = <string>import.meta.env.VITE_BACKEND_API_URL
  console.log('API_ROOT_URL: ', API_ROOT_URL)

  function isEmpty(value: string | null): boolean {
    return value === null || value.trim()?.length === 0
  }

  let email: string | null = null
  let assemblyStrategy: AssemblyStrategy | null
  let lang0Code: string = ''
  let lang0ResourceTypes: string[] = []
  let lang0ResourceCodes: string[] = []
  let lang1Code: string = ''
  let lang1ResourceTypes: string[] = []
  let lang1ResourceCodes: string[] = []
  let lang2Code: string = ''
  let lang2ResourceTypes: string[] = []
  let lang2ResourceCodes: string[] = []

  // Button will toggle this value
  let showAnotherLang: boolean = false
  function handleAddLang() {
    showAnotherLang = true
  }
  let showAnotherLang2: boolean = false
  function handleAddLang2() {
    showAnotherLang2 = true
  }

  onMount(() => {
    reset()
  })

  const LANGUAGE_CODES_AND_NAMES: string = '/language_codes_and_names'
  const RESOURCE_TYPES_FOR_LANG: string = '/resource_types_for_lang/'
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

  async function getLang0ResourceTypes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_TYPES_FOR_LANG + langCode)
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

  async function getLang1ResourceTypes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_TYPES_FOR_LANG + langCode)
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

  // Language 2

  async function getLang2CodesAndNames(): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang2ResourceTypes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_TYPES_FOR_LANG + langCode)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  async function getLang2ResourceCodes(langCode: string): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + RESOURCE_CODES_FOR_LANG + langCode)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  let finished_document_url: string = ''

  function reset() {
    assemblyStrategy = null
    // Be careful to set email to null as API expects a null rather
    // than empty string if email is not provided by user.
    email = null
    lang0Code = ''
    lang0ResourceTypes = []
    lang0ResourceCodes = []
    lang1Code = ''
    lang1ResourceTypes = []
    lang1ResourceCodes = []
    lang2Code = ''
    lang2ResourceTypes = []
    lang2ResourceCodes = []
    hideWaitMessage()
    hideErrorMessage()
    finished_document_url = ''
    showAnotherLang = false
    showAnotherLang2 = false
    document.getElementById('email')?.focus()
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

  function submit() {
    let rr = []
    // Create resource_requests for lang0
    for (let resourceCode of <string[]>lang0ResourceCodes) {
      for (let resourceType of <string[]>lang0ResourceTypes) {
        rr.push({
          lang_code: lang0Code,
          resource_type: resourceType,
          resource_code: resourceCode
        })
      }
    }
    // Create resource_requests for lang1
    for (let resourceCode of <string[]>lang1ResourceCodes) {
      for (let resourceType of <string[]>lang1ResourceTypes) {
        rr.push({
          lang_code: lang1Code,
          resource_type: resourceType,
          resource_code: resourceCode
        })
      }
    }
    // Create resource_requests for lang2
    for (let resourceCode of <string[]>lang2ResourceCodes) {
      for (let resourceType of <string[]>lang2ResourceTypes) {
        rr.push({
          lang_code: lang2Code,
          resource_type: resourceType,
          resource_code: resourceCode
        })
      }
    }

    console.log('email: ', email)
    // Create the JSON structure to POST.
    let documentRequest = {
      // FIXME Test that email_address is handled correctly with respect to null
      email_address: email?.trim(), // !isEmpty(email) ? email.trim() : null,
      assembly_strategy_kind: assemblyStrategy,
      resource_requests: rr
    }
    console.log('document request: ', JSON.stringify(documentRequest, null, 2))
    if (errorMessage) {
      hideErrorMessage()
    }
    showWaitMessage()
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
        finished_document_url = data['finished_document_request_key']
        hideErrorMessage()
        hideWaitMessage()
      })
      .catch(err => {
        console.error('error: ', err)
        hideWaitMessage()
        // Currently we don't display this error to the user, but we could
        // display it alongside the canned generic error message.
        // errorMessageDetails = JSON.stringify(err)
        showErrorMessage()
      })
  }
</script>

<div class="container">
  <div class="forms">
    <div>
      <h2>{import.meta.env.VITE_TOP_H2_HEADER}</h2>

      <form on:submit|preventDefault={submit}>
        <div class="fields">
          <label for="email">{import.meta.env.VITE_EMAIL_LABEL}</label>
          <input type="text" name="email" id="email" bind:value={email} />
        </div>

        <AssemblyStrategyComponent bind:assemblyStrategy />

        <div class:langs0-invisible={assemblyStrategy === null}>
          <h3>{import.meta.env.VITE_LANG_0_HEADER}</h3>

          {#await getLang0CodesAndNames()}
            <LoadingIndicator />
          {:then data}
            <select bind:value={lang0Code} name="lang">
              {#each data as langCodeAndName}
                <option value={langCodeAndName[0]}>{langCodeAndName[1]}</option>
              {/each}
            </select>
          {:catch error}
            <p class="error">{error.message}</p>
          {/await}
        </div>

        {#if !isEmpty(lang0Code)}
          <div>
            {#await getLang0ResourceTypes(lang0Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_0_RESOURCE_TYPES_HEADER}</h3>
              {#each data as resourceType}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang0ResourceTypes}
                    name="lang0ResourceTypes"
                    value={resourceType}
                  />
                  {resourceType}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}

        {#if !isEmpty(lang0Code) && lang0ResourceTypes?.length > 0}
          <div>
            {#await getLang0ResourceCodes(lang0Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_0_RESOURCE_CODES_HEADER}</h3>
              {#each data as resourceCodeAndName}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang0ResourceCodes}
                    name="langResourceCodes"
                    value={resourceCodeAndName[0]}
                  />
                  {resourceCodeAndName[1]}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}

        {#if !isEmpty(lang0Code) && lang0ResourceTypes?.length > 0 && lang0ResourceCodes?.length > 0}
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
              <select bind:value={lang1Code} name="lang1">
                {#each data as value}
                  <option value={value[0]}>{value[1]}</option>
                {/each}
              </select>
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang1Code)}
          <div>
            {#await getLang1ResourceTypes(lang1Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_1_RESOURCE_TYPES_HEADER}</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang1ResourceTypes}
                    name="lang1ResourceTypes"
                    {value}
                  />
                  {value}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang1Code) && lang1ResourceTypes?.length > 0}
          <div>
            {#await getLang1ResourceCodes(lang1Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_1_RESOURCE_CODES_HEADER}</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang1ResourceCodes}
                    name="lang1ResourceCodes"
                    value={value[0]}
                  />
                  {value[1]}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang1Code) && lang1ResourceTypes?.length > 0 && lang1ResourceCodes?.length > 0}
          <button disabled={showAnotherLang2} on:click|preventDefault={handleAddLang2}
            >{import.meta.env.VITE_ADD_ANOTHER_LANGUAGE_BUTTON_TXT}</button
          >
        {/if}
        {#if showAnotherLang2}
          <div>
            <h3>{import.meta.env.VITE_LANG_2_HEADER}</h3>
            {#await getLang2CodesAndNames()}
              <LoadingIndicator />
            {:then data}
              <select bind:value={lang2Code} name="lang2">
                {#each data as value}
                  <option value={value[0]}>{value[1]}</option>
                {/each}
              </select>
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang2Code)}
          <div>
            {#await getLang2ResourceTypes(lang2Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_2_RESOURCE_TYPES_HEADER}</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang2ResourceTypes}
                    name="lang2ResourceTypes"
                    id="lang2ResourceTypes"
                    {value}
                  />
                  {value}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(lang2Code) && lang2ResourceTypes?.length > 0}
          <div>
            {#await getLang2ResourceCodes(lang2Code)}
              <LoadingIndicator />
            {:then data}
              <h3>{import.meta.env.VITE_LANG_2_RESOURCE_CODES_HEADER}</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={lang2ResourceCodes}
                    name="lang2ResourceCodes"
                    id="lang2ResourceCodes"
                    value={value[0]}
                  />
                  {value[1]}
                </label>
              {/each}
            {:catch error}
              <p class="error">{error.message}</p>
            {/await}
          </div>
        {/if}

        <div style="margin-top:3em">
          <button on:click|preventDefault={reset}>reset</button>
          <button type="submit">submit</button>
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
      {#if finished_document_url.length > 0}
        <div class="finished-document-url">
          <p>
            {import.meta.env.VITE_DOCUMENT_READY_MSG_PART1}
            <a href="{API_ROOT_URL}/pdfs/{finished_document_url}"
              >{import.meta.env.VITE_DOCUMENT_READY_LINK_TXT}</a
            >
            {import.meta.env.VITE_DOCUMENT_READY_MSG_PART2}
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(body) {
    font-family: Arial, Helvetica, sans-serif;
    background-color: #f3f3f3;
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
  .container {
    display: flex;
  }
  .error {
    color: red;
  }
</style>
