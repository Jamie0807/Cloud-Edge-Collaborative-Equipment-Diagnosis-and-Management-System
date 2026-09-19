package com.diagnostics.cloudapi;

/** 诊断事件接收结果。 */
public record IngestResult(Kind kind, DiagnosticEvent event) {
  public enum Kind {
    CREATED,
    DUPLICATE
  }
}
