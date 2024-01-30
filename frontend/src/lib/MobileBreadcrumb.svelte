<script lang="ts">
  import { PUBLIC_MAX_LANGUAGES } from '$env/static/public'
  import { page, navigating } from '$app/stores'
  import BackButton from '$lib/BackButton.svelte'
  import NextButton from '$lib/NextButton.svelte'
  import { langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import { resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import { langRegExp, bookRegExp, resourceTypeRegExp, settingsRegExp } from '$lib/utils'

  export let title: string
  export let stepLabel: string
  export let turnLangStepOn: boolean
  export let turnBookStepOn: boolean
  export let turnResourceTypeStepOn: boolean
  export let turnSettingsStepOn: boolean
  export let submitLanguages: Function
  export let submitBooks: Function
  export let submitResourceTypes: Function
  export let numLang0ResourceTypes: number
  export let numLang1ResourceTypes: number

  let MAX_LANGUAGES = PUBLIC_MAX_LANGUAGES as unknown as number
</script>

<div
  class="flex items-center justify-between text-xl text-xl
         font-semibold leading-8 text-[#B3B9C2] sm:hidden"
>
  <!-- mobile only page title -->
  <div>
    <h3 class="text-xl text-[#015AD9]">{title}</h3>
    <h4 class="text-xl text-[#33445C]">Step {stepLabel}</h4>
  </div>
  <div class="flex items-center">
    <!-- back button logic -->
    {#if bookRegExp.test($page.url.pathname)}
      <BackButton url="/languages" />
    {:else if resourceTypeRegExp.test($page.url.pathname)}
      <BackButton url="/books" />
    {:else if settingsRegExp.test($page.url.pathname)}
      <BackButton url="/resource_types" />
    {:else}
      <button
        class="flex cursor-not-allowed items-center rounded-md border
                 border-[#E5E8EB] bg-white px-4 py-2
                 text-xl text-[#33445c]"
        disabled
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18.0374 10.5166H7.28489L11.9825 5.69276C12.3579 5.30724 12.3579 4.6746 11.9825 4.28908C11.8934 4.19744 11.7877 4.12474 11.6712 4.07514C11.5547 4.02553 11.4299 4 11.3038 4C11.1778 4 11.0529 4.02553 10.9365 4.07514C10.82 4.12474 10.7142 4.19744 10.6252 4.28908L4.28151 10.8033C4.19227 10.8948 4.12148 11.0034 4.07317 11.123C4.02486 11.2426 4 11.3707 4 11.5002C4 11.6297 4.02486 11.7579 4.07317 11.8774C4.12148 11.997 4.19227 12.1057 4.28151 12.1971L10.6252 18.7113C10.7143 18.8029 10.8201 18.8755 10.9366 18.925C11.053 18.9745 11.1778 19 11.3038 19C11.4299 19 11.5547 18.9745 11.6711 18.925C11.7876 18.8755 11.8934 18.8029 11.9825 18.7113C12.0716 18.6198 12.1423 18.5112 12.1905 18.3916C12.2388 18.272 12.2636 18.1439 12.2636 18.0144C12.2636 17.885 12.2388 17.7569 12.1905 17.6373C12.1423 17.5177 12.0716 17.4091 11.9825 17.3175L7.28489 12.4937H18.0374C18.5668 12.4937 19 12.0488 19 11.5052C19 10.9615 18.5668 10.5166 18.0374 10.5166Z"
            fill="#33445C"
          /></svg
        >
      </button>
    {/if}
    <!-- next button logic -->
    {#if langRegExp.test($page.url.pathname) && $langCountStore > 0 && $langCountStore <= MAX_LANGUAGES}
      <NextButton func={submitLanguages} />
    {:else if bookRegExp.test($page.url.pathname) && $bookCountStore > 0}
      <NextButton func={submitBooks} />
    {:else if resourceTypeRegExp.test($page.url.pathname) && (($langCountStore == 1 && $resourceTypesCountStore > 0) || ($langCountStore === 2 && numLang0ResourceTypes > 0 && numLang1ResourceTypes > 0))}
      <NextButton func={submitResourceTypes} />
    {:else}
      <button
        class="ml-2 flex cursor-not-allowed items-center rounded-md
                 border border-[#E5E8EB] bg-white px-4 py-2 text-xl text-[#33445c]"
        disabled
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
            fill="#001533"
          />
        </svg>
      </button>
    {/if}
  </div>
</div>

{#if turnLangStepOn && !turnBookStepOn && !turnResourceTypeStepOn && !turnSettingsStepOn}
  <div class="w-1/4 border border-[#015ad9] sm:hidden" />
{:else if turnBookStepOn && !turnResourceTypeStepOn && !turnSettingsStepOn}
  <div class="w-1/2 border border-[#015ad9] sm:hidden" />
{:else if turnResourceTypeStepOn && !turnSettingsStepOn}
  <div class="w-3/4 border border-[#015ad9] sm:hidden" />
{:else if turnSettingsStepOn}
  <div class="w-full border border-[#015ad9] sm:hidden" />
{/if}
