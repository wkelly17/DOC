<script lang="ts">
  function downloadFromUrl(url: string) {
    console.log(`url: ${url}`)
    window.open(url, '_blank')
  }
  export let url: string
  export let buttonText: string = 'Download PDF'
  export let buttonClass: string = 'btn orange-gradient w-5/6 rounded capitalize'
</script>

<button class={buttonClass} on:click={() => downloadFromUrl(url)}>
  <svg
    class="mr-3"
    width="15"
    height="17"
    viewBox="0 0 15 17"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M0.5 17H14.5V15H0.5V17ZM14.5 6H10.5V0H4.5V6H0.5L7.5 13L14.5 6Z"
      fill="#140E08"
    />
  </svg>{buttonText}</button
>

<style global lang="postcss">
  @tailwind base;
  @tailwind components;
  @tailwind utilities;

  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
</style>
