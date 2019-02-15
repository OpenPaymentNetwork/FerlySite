const prefix = 'api/'
// const baseUrl = host + prefix


export function post (urlTail, params = {}) {
  // const url = baseUrl + urlTail
  const url = prefix + urlTail
  fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(params)
  })
  // .then((response) => {
  //   console.log('response:', response)
  // })
}
