<script lang="ts">
  import { onMount } from 'svelte'
  let text: string = ''

  async function loop() {
    if (text.length === 3) text = ''
    text += '.'
    await new Promise(resolve => setTimeout(resolve, 300))
    loop()
  }

  onMount(() => {
    loop()
  })
</script>

<p>Loading{text}</p>
