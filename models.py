from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Meeting(BaseModel):
    days: str
    start_time: str
    end_time: str
    start_dt: str
    end_dt: str
    # bldg_cd: str
    # bldg_has_coordinates: bool
    # facility_descr: str
    # room: str
    # facility_id: str
    # instructor: str


class Model(BaseModel):
    # index: int
    # crse_id: str
    # crse_offer_nbr: int
    # strm: str
    # session_code: str
    # session_descr: str
    # class_section: str
    # location: str
    # location_descr: str
    start_dt: str
    end_dt: str
    # class_stat: str
    # campus: str
    # campus_descr: str
    # class_nbr: int
    # acad_career: str
    # acad_career_descr: str
    # component: str
    subject: str
    subject_descr: str
    catalog_nbr: str
    class_type: str
    # schedule_print: str
    # acad_group: str
    instruction_mode: str
    instruction_mode_descr: str
    # acad_org: str
    # grading_basis: str
    # wait_tot: int
    # wait_cap: int
    # class_capacity: int
    # enrollment_total: int
    # enrollment_available: int
    # descr: str
    # rqmnt_designtn: str
    # units: str
    # combined_section: str
    # enrl_stat: str
    # enrl_stat_descr: str
    # topic: str
    # section_type: str
    meetings: Optional[List[Meeting]]
    # crse_attr: str
    # crse_attr_value: str
    # reserve_caps: List
    # isInCart: bool
    # isEnrolled: bool
    # isWaitlisted: bool
    # notes: List
    # icons: List

