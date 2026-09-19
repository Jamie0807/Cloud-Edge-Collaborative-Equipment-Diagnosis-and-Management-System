package com.diagnostics.cloudapi;

/** 同一个 eventId 携带了不一致的业务载荷。 */
public class IdempotencyConflictException extends RuntimeException {
  public IdempotencyConflictException(String eventId) {
    super("eventId 幂等冲突: " + eventId);
  }
}
