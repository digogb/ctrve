import { useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const MSG_021 =
  "Existem dados não salvos neste formulário. Deseja sair sem salvar?";

export function useUnsavedChanges(isDirty: boolean) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isDirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = '';
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isDirty]);

  const guardedNavigate = useCallback(
    (to: string | number) => {
      if (isDirty && !window.confirm(MSG_021)) return;
      if (typeof to === "number") navigate(to);
      else navigate(to);
    },
    [isDirty, navigate]
  );

  return { guardedNavigate };
}
