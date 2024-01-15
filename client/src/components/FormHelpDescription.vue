<template>
  <div class="help-description">
    <p>{{ text }}</p>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss">
.help-description {
  border-left: 4px solid teal;
  padding: 10px 20px;
  margin: 10px 0;
  font-size: 0.9em;

  p {
    margin: 0;
  }
}
</style>
