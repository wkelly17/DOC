<script lang="ts">
  function downloadFromUrl(url: string) {
    console.log(`url: ${url}`)
    window.open(url, '_blank')
  }
  export let url: string
  export let buttonText: string = 'Download PDF'
  export let buttonClass: string = 'text-center p-4 blue-gradient w-1/2 rounded-md text-white'
</script>

<button class={buttonClass} on:click={() => downloadFromUrl(url)}>
  {buttonText}</button
>

<style global lang="postcss">
  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
  * :global(.blue-gradient) {
    background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%),
    linear-gradient(0deg, #33445C, #33445C);
  }
</style>
