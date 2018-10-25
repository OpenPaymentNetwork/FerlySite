// const host =
// const host = 'http://ferlyenv.bkk9wx3qnc.us-east-2.elasticbeanstalk.com/'
// const host = 'http://10.1.10.6:44225/'
const prefix = 'api/'
const baseUrl = host + prefix


export function post (urlTail, params = {}) {
  // const url = baseUrl + urlTail
  const url = prefix + urlTail
  // const url = prefix + urlTail
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
