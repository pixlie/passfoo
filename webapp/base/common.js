import * as constants from './constants';


export const requestHeaders = (method = 'GET', data) => {
  const myHeaders = new Headers();

  let authData = localStorage.getItem(constants.LOCALSTORAGE_VAR_NAME);
  if (authData && authData !== 'undefined' && authData !== undefined && authData !== '') {
    authData = JSON.parse(authData);
    myHeaders.append('Authorization', `Bearer ${authData.auth_token}`);
  }

  const request = {
    method,
    headers: myHeaders,
  };

  if ((method === 'POST' && data) || (method === 'PUT' && data)) {
    if (data.filter) {
      const toSend = data.filter(value => (value !== undefined && value !== null));
      request.body = JSON.stringify(toSend.toJS());
    } else {
      request.body = JSON.stringify(data);
    }
  }
  return request;
};
