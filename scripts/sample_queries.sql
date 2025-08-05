-- Total Records by File

                SELECT 
                    file_source,
                    count() as record_count
                FROM ocsf_data.ocsf_events 
                GROUP BY file_source 
                ORDER BY record_count DESC
                

-- Activity Types

                SELECT 
                    activity_name,
                    count() as count
                FROM ocsf_data.ocsf_events 
                WHERE activity_name IS NOT NULL
                GROUP BY activity_name 
                ORDER BY count DESC
                

-- Authentication Events

                SELECT 
                    time,
                    activity_name,
                    status,
                    src_endpoint_ip,
                    dst_endpoint_ip
                FROM ocsf_data.ocsf_events 
                WHERE class_name = 'Authentication'
                ORDER BY time DESC
                LIMIT 20
                

-- Network Activity

                SELECT 
                    time,
                    activity_name,
                    src_endpoint_ip,
                    dst_endpoint_ip,
                    dst_endpoint_port
                FROM ocsf_data.ocsf_events 
                WHERE class_name = 'DNS Activity' OR class_name = 'Network Activity'
                ORDER BY time DESC
                LIMIT 20
                

-- Failed Authentication Attempts

                SELECT 
                    time,
                    activity_name,
                    status_detail,
                    user_name,
                    src_endpoint_ip
                FROM ocsf_data.ocsf_events 
                WHERE status = 'Failure' AND class_name = 'Authentication'
                ORDER BY time DESC
                LIMIT 20
                

