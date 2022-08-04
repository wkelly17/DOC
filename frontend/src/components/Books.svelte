<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  import otBooks from '../data/ot_books'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import { extractLanguageCode, getSharedResourceCodes } from '../lib/requests'

  let sharedLangResourceCodes: string[] = []

  // Get the part of the lang name and code store that we want to use
  // reactively.
  $: lang0Code = $lang0NameAndCode.toString().split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.toString().split(',')[1]?.split(': ')[1]
  // Get the part of the lang name and code store that we want to show
  // reactively.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[0]
</script>

{#if $lang0NameAndCode && $lang1NameAndCode}
  <div>
    {#await getSharedResourceCodes(lang0Code, lang1Code)}
      <LoadingIndicator />
    {:then data}
      {@const otBooksInChosen = data.filter(function (element) {
        return otBooks.includes(element[0])
      })}
      {@const ntBooksInChosen = data.filter(function (element) {
        return !otBooks.includes(element[0])
      })}
      <h3>
        {import.meta.env.VITE_RESOURCE_CODES_HEADER}
        {#if $lang1NameAndCode}in common{/if} for {#if $lang1NameAndCode}languages:{:else}language:{/if}
        {lang0Name}{#if $lang1NameAndCode}, {lang1Name}{/if}
      </h3>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <h3>Old Testament</h3>
          <ul>
            {#each otBooksInChosen as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-ot-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-ot-{i}"
                  type="checkbox"
                  bind:group={sharedLangResourceCodes}
                  value={resourceCodeAndName[0]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
        <div>
          <h3>New Testament</h3>
          <ul>
            {#each ntBooksInChosen as resourceCodeAndName, i}
              <li>
                <label for="lang-resourcecode-nt-{i}">{resourceCodeAndName[1]}</label>
                <input
                  id="lang-resourcecode-nt-{i}"
                  type="checkbox"
                  bind:group={sharedLangResourceCodes}
                  value={resourceCodeAndName[0]}
                  class="checkbox"
                />
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {:catch error}
      <p class="error">{error.message}</p>
    {/await}
  </div>
{/if}
