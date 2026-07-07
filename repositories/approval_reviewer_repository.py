from models.approval_request import ApprovalRequest
from models.approval_reviewer import ApprovalReviewer
from repositories.base_repository import AsyncRepository


class ApprovalReviewerRepository(AsyncRepository):
    model = ApprovalReviewer

    async def create_many(
        self,
        request: ApprovalRequest,
        reviewer_user_ids: list[str],
    ) -> list[ApprovalReviewer]:
        reviewers = [
            ApprovalReviewer(
                request=request,
                reviewer_user_id=reviewer_id,
            )
            for reviewer_id in reviewer_user_ids
        ]

        self.session.add_all(reviewers)
        await self.session.flush()

        return reviewers