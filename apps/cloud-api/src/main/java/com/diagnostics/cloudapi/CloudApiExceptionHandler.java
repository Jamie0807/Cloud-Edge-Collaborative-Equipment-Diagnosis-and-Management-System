package com.diagnostics.cloudapi;

import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 统一输出可区分的业务错误。 */
@RestControllerAdvice
public class CloudApiExceptionHandler {
  @ExceptionHandler(IdempotencyConflictException.class)
  public org.springframework.http.ResponseEntity<Map<String, String>> handleConflict(
      IdempotencyConflictException exception) {
    return org.springframework.http.ResponseEntity.status(HttpStatus.CONFLICT)
        .body(Map.of("code", "IDEMPOTENCY_CONFLICT", "message", exception.getMessage()));
  }

  @ExceptionHandler(IllegalArgumentException.class)
  public org.springframework.http.ResponseEntity<Map<String, String>> handleInvalid(
      IllegalArgumentException exception) {
    return org.springframework.http.ResponseEntity.badRequest()
        .body(Map.of("code", "VALIDATION_ERROR", "message", exception.getMessage()));
  }
}
