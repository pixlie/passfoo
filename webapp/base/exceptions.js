export class FetchException {
  constructor(typeOfException, message) {
    this.code = typeOfException;
    this.message = message;
  }
}
