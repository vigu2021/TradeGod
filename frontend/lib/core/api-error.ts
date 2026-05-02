// Typed error class, every failed API call throws this via the response interceptor.
export class ApiError extends Error {
  constructor(
    public code: string,
    public statusCode: number,
    public detail?: string,
  ) {
    super(detail ?? code);
    this.name = "ApiError";
  }
}
