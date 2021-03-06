from canvasaio.canvas_object import CanvasObject
from canvasaio.progress import Progress
from canvasaio.util import combine_kwargs


class SisImport(CanvasObject):
    def __str__(self):  # pragma: no cover
        return "{} ({})".format(self.workflow_state, self.id)

    async def abort(self, **kwargs):
        """
        Abort this SIS import.

        :calls: `PUT /api/v1/accounts/:account_id/sis_imports/:id/abort \
        <https://canvas.instructure.com/doc/api/sis_imports.html#method.sis_imports_api.abort>`_

        :rtype: :class:`canvasaio.sis_import.SisImport`
        """
        response = await self._requester.request(
            "PUT",
            "accounts/{}/sis_imports/{}/abort".format(self.account_id, self.id),
            _kwargs=combine_kwargs(**kwargs),
        )
        return SisImport(self._requester, await response.json())

    async def restore_states(self, **kwargs):
        """
        Restore workflow_states of SIS imported items.

        :calls: `PUT /api/v1/accounts/:account_id/sis_imports/:id/restore_states \
        <https://canvas.instructure.com/doc/api/sis_imports.html#method.sis_imports_api.restore_states>`_

        :rtype: :class:`canvasaio.progress.Progress`
        """
        response = await self._requester.request(
            "PUT",
            "accounts/{}/sis_imports/{}/restore_states".format(
                self.account_id, self.id
            ),
            _kwargs=combine_kwargs(**kwargs),
        )
        return Progress(self._requester, await response.json())
