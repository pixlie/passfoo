import { requestHeaders } from '../base/common';
import { FetchException } from '../base/exceptions';


export const fetchQuestionList = (setter) => {
  fetch("/api/q", requestHeaders())
    .then((response) => {
        if (response.status === 200) {
          return response.json();
        }
        throw new FetchException(`HTTP_${response.status}`);
      })
    .then((data) => {
      setter(data);
    })
}